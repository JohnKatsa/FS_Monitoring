#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/param.h>
#include <sys/stat.h>

int curr_fd;
int curr_offset;

int hex_to_dec(char* hexVal){

  int len = strlen(hexVal);
  // Initializing base value to 1, i.e 16^0
  int base = 1;
  int dec_val = 0;

  // Extracting characters as digits from last character
  for (int i=len-1; i>=0; i--){
      // if character lies in '0'-'9', converting
      // it to integral 0-9 by subtracting 48 from
      // ASCII value.
      if (hexVal[i]>='0' && hexVal[i]<='9'){
          dec_val += (hexVal[i] - 48)*base;
          // incrementing base by power
          base = base * 16;
      }
      // if character lies in 'A'-'F' , converting
      // it to integral 10 - 15 by subtracting 55
      // from ASCII value
      else if (hexVal[i]>='A' && hexVal[i]<='F'){
          dec_val += (hexVal[i] - 55)*base;
          // incrementing base by power
          base = base*16;
      }
  }

  return dec_val;
}

int write_result(char* syscall_num, char* filename, char* a0, char* a1,
  char* a2, char* a3, FILE* fsout){

  //early prunning (if number, thus no name (and no action made) or null)
  if((filename == NULL) || ((filename[0] >= 48) && (filename[0] <= 57)))
    return 0;

  // get real number
  int n = atoi(syscall_num);

  if(n == 0){ // read
    int pos = 0, size;
    // lseek was used before this call
    if(curr_fd == hex_to_dec(a0)){
      pos = curr_offset;
    }
    fprintf(fsout, "READ\t %s\t %d\t %d\n", filename, pos, hex_to_dec(a2));
  }
  if(n == 1){ // write
    int pos = 0, size;
    // lseek was used before this call
    if(curr_fd == hex_to_dec(a0)){
      pos = curr_offset;
    }
    fprintf(fsout, "WRITE\t %s\t %d\t %d\n", filename, pos, hex_to_dec(a2));
  }
  if(n == 2){ // open
    fprintf(fsout, "OPEN\t %s\n", filename);
  }
  if(n == 3){ // close
    fprintf(fsout, "CLOSE\t %s\n", filename);
  }
  if(n == 8){ // lseek called (need to update global current statistics)
    if(hex_to_dec(a0) == curr_fd)
      curr_offset += hex_to_dec(a1);
    else{
      curr_fd = hex_to_dec(a0);
      curr_offset = hex_to_dec(a1);
    }
  }

  return 0;
}

int main(int argc, char** argv)
{
  size_t len = 0;
  ssize_t n;
  char* buffer = NULL;
  const char delimeters[5] = " \t,=";

  char* input = argv[1];
  char* output = argv[2];

  FILE* fs = fopen(input, "r");
  FILE* fsout = fopen(output, "w+");

  // write at beginning of file headers
  fprintf(fsout,"System Call\tFile Name\tPosition\tSize\n");

  char* filename = NULL;
  char* proctitle = NULL;
  char* syscall_num;
  char* a0;
  char* a1;
  char* a2;
  char* a3;

  int flag = 0;

  // break file in lines
  while ((n = getline(&buffer, &len, fs)) != -1) {

    // break lines in words
    char* token = strtok(buffer, delimeters);
    while(token != NULL){
      //search for arguments
      char* temp;

      if(((temp = strstr(token,"proctitle")) != NULL)){
        token = strtok(NULL, delimeters);
        proctitle = malloc(strlen(token)+1);
        memcpy(proctitle,token,strlen(token)+1);
        if(strlen(proctitle)-1 >= 1)
          proctitle[strlen(proctitle)-1] = '\0';
      }
      // find what is the filename
      if(((temp = strstr(token,"name")) != NULL) && !flag){
        token = strtok(NULL, delimeters);
        filename = malloc(strlen(token)+1);
        memcpy(filename,token,strlen(token)+1);
        if(strlen(filename)-1 >= 1)
          filename[strlen(filename)-1] = '\0';
        flag = 1;
      }
      // find which syscall is
      if((temp = strstr(token,"syscall")) != NULL){
        token = strtok(NULL, delimeters);
        syscall_num = token;
      }
      // argument 0
      if((temp = strstr(token,"a0")) != NULL){
        token = strtok(NULL, delimeters);
        a0 = token;
      }
      // argument 1
      if((temp = strstr(token,"a1")) != NULL){
        token = strtok(NULL, delimeters);
        a1 = token;
      }
      // argument 2
      if((temp = strstr(token,"a2")) != NULL){
        token = strtok(NULL, delimeters);
        a2 = token;
      }
      // argument 3
      if((temp = strstr(token,"a3")) != NULL){
        token = strtok(NULL, delimeters);
        a3 = token;
        // when we get in a3 we are done and we have all the data we need. Its time to write to file
        if(filename == NULL){
          filename = proctitle;
          proctitle = NULL;
        }
        write_result(syscall_num,filename,a0,a1,a2,a3,fsout);
        if(filename != NULL)
          free(filename);
        if(proctitle != NULL)
          free(proctitle);
        filename = NULL;
        proctitle = NULL;
      }

      token = strtok(NULL, delimeters);
    }
    flag = 0;

  }
  fclose(fs);
  fclose(fsout);

  return 0;
}
