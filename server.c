#include <sys/types.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>

#define SERVER_PORT 1234
#define QUEUE_SIZE 5
#define MAX_TOPICS 10
#define MAX_USERS 3

pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

pthread_t threads[MAX_USERS];
int connection_client_descriptors[MAX_USERS];
char topics[MAX_TOPICS][10];
int num_of_topics;
int subscriptions[MAX_USERS][MAX_TOPICS] = {0};


//struktura zawierająca dane, które zostaną przekazane do wątku
struct thread_data_t
{
    int serverStatus;
    int socket_nr;
    char tekst[111];
};

struct message
{
    char akcja;
    char tytul[10];
    char tekst[100];
};


int readError(int flag)
{
    if (flag == -1)
    {
        fprintf(stderr, "Błąd przy próbie odczytania wiadomosci.\n");
    }
    else if (flag == 0)
    {
        fprintf(stderr, "Gniazdo jest zamknięte.r\n");
    }
    return flag;
}

int writeError(int flag)
{
    if (flag == -1)
    {
        fprintf(stderr, "Błąd przy próbie wysłania wiadomosci.\n");
    }
    else if (flag == 0)
    {
        fprintf(stderr, "Gniazdo jest zamknięte.w\n");
    }
    return flag;
}


int topicExist(char topic[10])
{
    for(int i = 0; i < MAX_TOPICS; i ++)
    {
        if(strncmp(topics[i], topic, 10) == 0)
            return i;
    }
    return -1;
}


int addConnection(int client)
{
    for (int i = 0; i < MAX_USERS; i++)
    {
        if (connection_client_descriptors[i] == -1)
        {
            connection_client_descriptors[i] = client;
            fprintf(stderr, "Nawiązano nowe połączenie!\n");
            return i;
        }
    }
    fprintf(stderr, "Serwer jest pełny!\n");
    write(client, "exit\n", 100);
    return -1;
}


void printSubs()
{
    for(int i = 0; i < MAX_USERS; i++)
    {
        for(int j = 0; j < MAX_TOPICS; j++)
        {
            printf("%d ", subscriptions[i][j]);
        }
        printf("\n");
    }
}


//funkcja opisującą zachowanie wątku - musi przyjmować argument typu (void *) i zwracać (void *)
void *ThreadBehavior(void *t_data)
{
    pthread_detach(pthread_self());
    struct thread_data_t *th_data = (struct thread_data_t *)t_data;

    int nr = (*th_data).socket_nr;

    while (1)
    {
        if ((*th_data).serverStatus == 0)
        {
            break;
        }
        //pthread_mutex_lock(&m);
        int errR = readError(read(connection_client_descriptors[nr], (*th_data).tekst, sizeof((*th_data).tekst)));
        //pthread_mutex_unlock(&m);
        if (errR == -1)
        {
            exit(1);
        }
        else if (errR == 0)
        {
            connection_client_descriptors[nr] = -1;
            break;
        }
        else
        {
            struct message mess;
            mess.akcja = (*th_data).tekst[0];
            for(int i = 1; i < 11; i++)
            {
                mess.tytul[i - 1] = (*th_data).tekst[i];
            }
            for(int i = 11; i < 111; i++)
            {
                mess.tekst[i - 11] = (*th_data).tekst[i];
            }
            //printf("Akcja: %c,\nTytul: %s,\nTresc: %s", mess.akcja, mess.tytul, mess.tekst);

            // Rozlaczenie z serwerem
            if(strncmp((*th_data).tekst, "e", 1) == 0)
            {
                printf("Rozloczono klienta o numerze: %d\n", nr);
                // Wyzerowanie subskrypcji
                for(int i = 0; i < MAX_TOPICS; i++)
                {
                    subscriptions[nr][i] = 0;
                }
                write(connection_client_descriptors[nr], (*th_data).tekst, sizeof((*th_data).tekst));
                connection_client_descriptors[nr] = -1;
                break;
            }
            // Wyslanie wiadomosci
            if(strncmp((*th_data).tekst, "s", 1) == 0)
            {
            int topic_index = topicExist(mess.tytul);
            for (int j = 0; j < MAX_USERS; j++)
                {
                    if (j != nr && connection_client_descriptors[j] != -1 && subscriptions[j][topic_index] == 1)
                    {
                        printf("Wysylam wiadomosc o temacie %s do %d\n", topics[topic_index], j);
                        printf("%s\n", (*th_data).tekst);
                        //pthread_mutex_lock(&m);
                        int errW = writeError(write(connection_client_descriptors[j], (*th_data).tekst, sizeof((*th_data).tekst)));
                        //pthread_mutex_unlock(&m);
                        if (errW == -1)
                        {
                            exit(1);
                        }
                        else if (errW == 0)
                        {
                            connection_client_descriptors[j] = -1;
                            break;
                        }
                    }
                }
            }
            // Dodanie tematu
            if(strncmp((*th_data).tekst, "a", 1) == 0)
            {        
                if(num_of_topics < MAX_TOPICS)
                {
                    if(topicExist(mess.tytul) != -1)
                    {
                        printf("Istniej juz temat o podanej nazwie!\n");
                    }
                    else
                    {
                        strcpy(topics[num_of_topics], mess.tytul);
                        printf("Dodano nowy temat: %s\n", topics[num_of_topics]);
                        num_of_topics++;
                        for(int i = 0; i < num_of_topics; i++)
                        {
                            printf("Temat %d: %s\n", i, topics[i]);
                        }
                    }
                }
                else
                {
                    printf("Przekroczono maksymalna ilosc tematow!\n");
                }
            }
            // Subskrypcja tematu
            if(strncmp((*th_data).tekst, "f", 1) == 0)
            {
                int index = topicExist(mess.tytul);
                if(index != -1)
                {
                    if(subscriptions[nr][index] == 1)
                    {
                        printf("Uzytkownik %d juz subskrybuje temat %s!\n", nr, topics[index]);
                    }
                    else
                    {
                        subscriptions[nr][index] = 1;
                        printSubs();
                    }
                }
                else
                {
                    printf("Podany temat nie istnieje!\n");
                }
            }
            // Anulowanie Subskrypcji
            if(strncmp((*th_data).tekst, "u", 1) == 0)
            {
                int index = topicExist(mess.tytul);
                if(index != -1)
                {
                    if(subscriptions[nr][index] == 0)
                    {
                        printf("Uzytkownik %d nie subskrybuje tematu %s!\n", nr, topics[index]);
                    }
                    else
                    {
                        subscriptions[nr][index] = 0;
                        printSubs();
                    }
                }
                else
                {
                    printf("Podany temat nie istnieje!\n");
                }
            }
        }
    }
    pthread_exit(NULL);
}

int main(int argc, char *argv[])
{
    int server_socket_descriptor;
    int connection_socket_descriptor;
    int bind_result;
    int listen_result;
    char reuse_addr_val = 1;
    struct sockaddr_in server_address;

    strcpy(topics[0], "football");
    strcpy(topics[1], "e-sport");
    strcpy(topics[2], "books");
    strcpy(topics[3], "computers");

    num_of_topics = 4;

    //inicjalizacja gniazda serwera

    memset(&server_address, 0, sizeof(struct sockaddr));
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = htonl(INADDR_ANY);
    server_address.sin_port = htons(SERVER_PORT);

    server_socket_descriptor = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket_descriptor < 0)
    {
        fprintf(stderr, "%s: Błąd przy próbie utworzenia gniazda..\n", argv[0]);
        exit(1);
    }
    setsockopt(server_socket_descriptor, SOL_SOCKET, SO_REUSEADDR, (char *)&reuse_addr_val, sizeof(reuse_addr_val));

    bind_result = bind(server_socket_descriptor, (struct sockaddr *)&server_address, sizeof(struct sockaddr));
    if (bind_result < 0)
    {
        fprintf(stderr, "%s: Błąd przy próbie dowiązania adresu IP i numeru portu do gniazda.\n", argv[0]);
        exit(1);
    }

    listen_result = listen(server_socket_descriptor, QUEUE_SIZE);
    if (listen_result < 0)
    {
        fprintf(stderr, "%s: Błąd przy próbie ustawienia wielkości kolejki.\n", argv[0]);
        exit(1);
    }

    for (int i = 0; i < sizeof(connection_client_descriptors) / sizeof(int); i++)
        connection_client_descriptors[i] = -1;

    // printf("Sizeof connection client descriptors: %ld\n", sizeof(connection_client_descriptors));

    struct thread_data_t *t_data = malloc(sizeof(struct thread_data_t));
    (*t_data).serverStatus = 1;

    while (1)
    {
        connection_socket_descriptor = accept(server_socket_descriptor, NULL, NULL);
        if (connection_socket_descriptor < 0)
        {
            fprintf(stderr, "%s: Błąd przy próbie utworzenia gniazda dla połączenia.\n", argv[0]);
            exit(1);
        }
        int nr = addConnection(connection_socket_descriptor);
        for (int i = 0; i < MAX_USERS; i++)
            printf("Klient id: %d\n", connection_client_descriptors[i]);
        if (nr >= 0)
        {
            
            (*t_data).socket_nr = nr;
            int create_result = pthread_create(&threads[nr], NULL, ThreadBehavior, (void *)t_data);
            if (create_result)
            {
                printf("Błąd przy próbie utworzenia wątku, kod błędu: %d\n", create_result);
                (*t_data).serverStatus = 0;
                exit(-1);
            }
        }
    }

    close(server_socket_descriptor);
    return (0);
}
