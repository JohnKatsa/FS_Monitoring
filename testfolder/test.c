#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>

int main()
{
  char buf[100];

  int fd1 = open("testinput.txt", O_RDWR | O_APPEND);
  if(fd1 < 0)
    perror("Bad file name");

  ssize_t readBytes = read(fd1,buf,40);
  if(readBytes == 40)
    printf("Read 40 bytes\n");

  char buf2[11] = "character\n";

  ssize_t writeBytes = write(fd1,buf2,10);
  if(writeBytes == 10)
    printf("Wrote 10 bytes\n");

  int pid = fork();

  // original process - parent
  if(pid > 0){
    ssize_t readBytes = read(fd1,buf,10);
    if(readBytes == 10)
      printf("Parent: %d , Read 40 bytes\n", getpid());
    else
      perror("Can't read");

    int fd2 = dup(fd1);
    if(fd2 <= 0)
      perror("Didn't dup");

    ssize_t writeBytes = write(fd2,buf2,10);
    if(writeBytes == 10)
      printf("Parent: %d , Wrote 10 bytes\n", getpid());

    close(fd1);
    close(fd2);
  }
  // child process
  else if(pid == 0){
    ssize_t writeBytes = write(fd1,"buf2",10);
    if(writeBytes == 10)
      printf("Child: %d , Wrote 10 bytes\n", getpid());

    off_t ret = lseek(fd1,2,SEEK_SET);
    if(ret == -1)
      perror("Failed to seek in file");
    ret = lseek(fd1,12,SEEK_SET);
    if(ret == -1)
      perror("Failed to seek in file");

    close(fd1);
  }
  else
    perror("Unable to fork");

  return 0;
}
