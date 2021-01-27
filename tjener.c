#include <arpa/inet.h>
#include <unistd.h> 
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

#define LOKAL_PORT 80
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler 

int main ()
{
	
  struct sockaddr_in  lok_adr;
  // Fildeskriptor variablene som brukes for socketene
  int sd, ny_sd;
  // PID (Prosessindikator)
  pid_t pid;
  // Ett buffer for innlesing fra fil
  char fbuffer[1024];
  // Ett buffer for innlesing fra fildeskriptor
  char fdbuffer[1024];
  // Streng som inneholder feilmelding om ikke-støttet filtype
  char nosupmedia[] = "415 Unsupported Media Type\n\nThe request includes a media that the server doesn't support\n";
  // Streng som inneholder feilmelding om at fil ikke eksisterer
  char noresource[] = "404 File not found\n";
  // Peker av typen fil
  FILE * fp;
  
  // Endre rotkatalog for kallende prosess 
  if(chroot("home/lloyd/da-nan3000/eksempler/www/") == 0)
	printf("The root catalogue was changed");
  
  // Setter opp socket-strukturen
  sd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  
  if(sd == -1)
	fprintf(stderr, "Could not create socket\n");
  else
	fprintf(stderr, "Socket created successfully\n");

  // For at operativsystemet ikke skal holde porten reservert etter tjenerens død
  setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int));

  // Initierer lokal adresse
  lok_adr.sin_family      = AF_INET;
  lok_adr.sin_port        = htons((u_short)LOKAL_PORT); 
  lok_adr.sin_addr.s_addr = htonl(         INADDR_ANY);

  // Kobler sammen socket og lokal adresse
  if ( 0==bind(sd, (struct sockaddr *)&lok_adr, sizeof(lok_adr)) )
    fprintf(stderr, "Prosess %d er knyttet til port %d.\n", getpid(), LOKAL_PORT);
  else
    exit(1);
    
  // Privilegie-separasjon, frata serveren root-rettigheter før lytting
  if(setgid(getgid()) != 0)
	printf("setgid not set\n");
  if(setuid(getuid()) != 0)
	printf("setuid not set\n");
  
  // Venter på forespørsel om forbindelse
  listen(sd, BAK_LOGG); 
  while(1){ 

    // Aksepterer mottatt forespørsel
    ny_sd = accept(sd, NULL, NULL);    

	pid = fork();
    if(0 == pid ) {
		/*printf("PID of child process is %d\n", pid);
		pid_t ppid = getppid();
		printf("PID of parent process shown from child is %d\n", ppid);*/
	  close(sd);
      dup2(ny_sd, 1); // redirigerer socket til standard utgang
      
      // Les melding fra socket og plasser i egnet buffer
      read(ny_sd, fdbuffer, sizeof(fdbuffer));
      
      // Hva havner i fdbuffer?
      // printf("%s \n", fdbuffer);
      
      // Se gjennom GET-forespørselen og avgjør om det letes 
      // etter asis-fil. Hvis svaret er nei, skriv ut feilmelding
      char * test;
      char * saveptr = fdbuffer;
      test = strtok_r(fdbuffer, ".", &saveptr);
      //printf("Test is %s\n", test);
      test = strtok_r(NULL, " ", &saveptr);
      //printf("Test is %s\n", test);
      if(strcmp(test, "asis") == 0){
		  /* Må avgjøre om filstien finnes 
		   * og kan aksesseres, ellers sendes feilmelding */
		  char * test2;
		  char * test3;
		  test2 = strtok_r(fdbuffer, " ", &saveptr);
		  //printf("Test2 is %s\n", test2);
		  test3 = strtok_r(NULL, " ", &saveptr);
		  //printf("Test3 is %s\n", test3);
		  test2 = ".asis";
		  strcat(test3, test2);
		  //printf("Test3 is %s\n", test3);
		  if(access(test3, F_OK) == 0){
			  //printf("%s exists\n", test3);
			  /* Vet nå at filsti er gyldig og at filtype er OK
			   * Åpner filen */
			  fp = fopen(test3, "r");
			  if(fp == NULL){
				  //printf("The file '%s' failed to open \n", filepath);
				  }
			  else{
				  //printf("The file '%s' was opened successfully \n", filepath);
				  int obj = fread(fbuffer, 1, 1024, fp);
				  
				  //printf("Content of fbuffer is %s\n", fbuffer);
				  write(ny_sd, fbuffer, obj);
				  }
				// Les tekststrenger fra filen, plasser det i et buffer og skriv ut
				//while(fscanf(fp, "%s", fbuffer)!=EOF){
				//printf("%s", fbuffer);
				//}		
		  }
		  else{
			write(ny_sd, noresource, strlen(noresource));
		  }
	  }
	  else{
		  write(ny_sd, nosupmedia, strlen(nosupmedia));
	  }
 
      // Sjekk om filen eksisterer, deretter åpne index.asis filen
      //fp = fopen(filepath, "r");
      /*if(fp == NULL){
		  printf("The file '%s' failed to open \n", filepath);
	  }
	  else{
		  printf("The file '%s' was opened successfully \n", filepath);
	  }*/
      
      // Avslutter lesing av fil
      fclose(fp);
      
      // Flusher bufferet knyttet til stdout
      fflush(stdout);

      // Sørger for å stenge socket for skriving og lesing (SHUT_RDWR)
      // NB! Frigjør ingen plass i fildeskriptortabellen
      shutdown(ny_sd, SHUT_RDWR);
      exit(0);
    }

    else {
      close(ny_sd);
      //printf("PID of parent process is %d\n", pid);
    }
  }
  return 0;
}

/*printf("HTTP/1.1 200 OK\n");
      printf("Content-Type: text/plain\n");
      printf("\n");
      printf("HTTP/1.1 200 OK\nHei Anne-Marthe uwu!\nJeg synes data er goy!\n");
      */
