// #include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>

#define BUF_SIZE 1024
#define NUM_THREADS 5

void func(int sockfd)
{
   char buff[111];
   char action[BUFSIZ];
   char title[10];
   char text[100];
   int pid = fork();
   if (pid == 0)
   {
      int input_value;
      while (1)
      {
         // bzero(buff, sizeof(buff));
         printf("MENU\n"
         "1. Dodaj temat\n"
         "2. Wyslij wiadomosc\n"
         "3. Zasubskrybuj temat\n"
         "4. Anuluj Subskrypcje\n"
         "0. Wyjscie\n"
         "Podaj opcje: ");
         fgets(action, sizeof(action), stdin);
         input_value = atoi(action);
         switch (input_value)
         {
         case 1:
            buff[0] = 'a';
            printf("Podaj tytul: ");
            fgets(title, sizeof(title), stdin);
            title[strcspn(title, "\n")] = 0;
            for (int i = 1; i < 11; i++)
            {
               buff[i] = title[i - 1];
            }
            write(sockfd, buff, sizeof(buff));
            bzero(buff, sizeof(buff));
            bzero(title, sizeof(title));
            bzero(text, sizeof(text));
            break;

         case 2:
            printf("Podaj tytul: ");
            fgets(title, sizeof(title), stdin);
            title[strcspn(title, "\n")] = 0;
            printf("Podaj tresc: ");
            fgets(text, sizeof(text), stdin);
            text[strcspn(text, "\n")] = 0;
            printf("Text: %s\n", text);
            buff[0] = 's';
            for (int i = 1; i < 11; i++)
            {
               buff[i] = title[i - 1];
            }
            for (int i = 11; i < 111; i++)
            {
               buff[i] = text[i - 11];
            }
            printf("%s \n", buff);
            write(sockfd, buff, sizeof(buff));
            bzero(buff, sizeof(buff));
            bzero(title, sizeof(title));
            bzero(text, sizeof(text));
            break;

         case 3:
            buff[0] = 'f';
            printf("Podaj tytul: ");
            fgets(title, sizeof(title), stdin);
            title[strcspn(title, "\n")] = 0;
            for (int i = 1; i < 11; i++)
            {
               buff[i] = title[i - 1];
            }
            write(sockfd, buff, sizeof(buff));
            bzero(buff, sizeof(buff));
            bzero(title, sizeof(title));
            bzero(text, sizeof(text));
            break;

         case 4:
            buff[0] = 'u';
            printf("Podaj tytul: ");
            fgets(title, sizeof(title), stdin);
            title[strcspn(title, "\n")] = 0;
            for (int i = 1; i < 11; i++)
            {
               buff[i] = title[i - 1];
            }
            write(sockfd, buff, sizeof(buff));
            bzero(buff, sizeof(buff));
            bzero(title, sizeof(title));
            bzero(text, sizeof(text));
            break;

         case 0:
            buff[0] = 'e';
            write(sockfd, buff, sizeof(buff));
            bzero(buff, sizeof(buff));
            break;

         default:
            break;
         }
      }
   }
   else
   {
      while (1)
      {
         bzero(buff, sizeof(buff));
         if (read(sockfd, buff, sizeof(buff)) > 0)
         {
            if ((strncmp(buff, "e", 1)) == 0)
            {
               printf("\nClient Exit...\n");
               kill(pid, SIGKILL);
               break;
            }
            printf("\n\tFrom Server : %s", buff);
         }
      }
   }
}

int main(int argc, char *argv[])
{
   int connection_socket_descriptor;
   int connect_result;
   struct sockaddr_in server_address;
   struct hostent *server_host_entity;
   printf("Start.\n");

   if (argc != 3)
   {
      fprintf(stderr, "Sposob uzycia: %s server_name port_number\n", argv[0]);
      exit(1);
   }

   server_host_entity = gethostbyname(argv[1]);
   if (!server_host_entity)
   {
      fprintf(stderr, "%s: Nie mozna uzyskac adresu IP serwera.\n", argv[0]);
      exit(1);
   }

   connection_socket_descriptor = socket(PF_INET, SOCK_STREAM, 0);
   if (connection_socket_descriptor < 0)
   {
      fprintf(stderr, "%s: Blad przy probie utworzenia gniazda.\n", argv[0]);
      exit(1);
   }

   memset(&server_address, 0, sizeof(struct sockaddr));
   server_address.sin_family = AF_INET;
   memcpy(&server_address.sin_addr.s_addr, server_host_entity->h_addr, server_host_entity->h_length);
   server_address.sin_port = htons(atoi(argv[2]));

   connect_result = connect(connection_socket_descriptor, (struct sockaddr *)&server_address, sizeof(struct sockaddr));
   if (connect_result < 0)
   {
      fprintf(stderr, "%s: Blad przy probie polaczenia z serwerem (%s:%i).\n", argv[0], argv[1], atoi(argv[2]));
      exit(1);
   }
   printf("Serwer socket descriptor: %d\n", connection_socket_descriptor);
   func(connection_socket_descriptor);
   close(connection_socket_descriptor);
   return 0;
}