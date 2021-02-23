#include <arpa/inet.h>
#include <unistd.h> 
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/socket.h>

#define LOKAL_PORT 80
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler 

void demoniser();

int main ()
{
	
  struct sockaddr_in  lok_adr;
  // Fildeskriptor variablene som brukes for socketene
  int sd, ny_sd, ed;
  // PID (Prosessindikator)
  pid_t pid;
  // Ett buffer for innlesing fra fil
  char fbuffer[1024];
  // Ett buffer for innlesing fra fildeskriptor
  char fdbuffer[1024];
  // Streng som inneholder feilmelding om ikke-støttet filtype
  char nosupmedia[1024] = "HTTP/1.1 415 Unsupported Media Type\n\nThe request includes a media that the server doesn't support\n";
  // Streng som inneholder feilmelding om at fil ikke eksisterer
  char noresource[1024] = "HTTP/1.1 404 File not found\n\nThe requested resource was not found.";
  // Peker av typen fil
  FILE * fp;
  
  // Omdirigere stderr(fildeskriptor 2) til å skrive til en loggfil
  ed = open("/var/log/debug.log", O_WRONLY);
  dup2(ed, 2);
  close(ed);
  
  // Endre rotkatalog for kallende prosess 
  if(chroot("/var/www/") == 0)
	fprintf(stderr, "The root catalogue was changed\n");
  else
	fprintf(stderr, "The root catalogue was not changed\n");
  
  // Setter opp socket-strukturen
  sd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  
  if(sd == -1)
	fprintf(stderr, "Could not create socket\n");
  else
	printf("Socket created successfully\n");

  // For at operativsystemet ikke skal holde porten reservert etter tjenerens død
  setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int));

  // Initierer lokal adresse
  lok_adr.sin_family      = AF_INET;
  lok_adr.sin_port        = htons((u_short)LOKAL_PORT); 
  lok_adr.sin_addr.s_addr = htonl(         INADDR_ANY);

  // Kobler sammen socket og lokal adresse
  if ( 0==bind(sd, (struct sockaddr *)&lok_adr, sizeof(lok_adr)) )
    printf("Prosess %d er knyttet til port %d.\n", getpid(), LOKAL_PORT);
  else
    exit(1);
    
  // Privilegie-separasjon, frata serveren root-rettigheter før lytting
  if(setgid(1000) != 0)
	fprintf(stderr, "setgid not set\n");
  if(setuid(1000) != 0)
	fprintf(stderr, "setuid not set\n");
	
  // Demoniserer prosessen
  if (getppid() != 1) {
	demoniser();
  }
  
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
	  //close(sd);
      dup2(ny_sd, 1); // redirigerer socket til standard utgang
      
      // Les melding fra socket og plasser i egnet buffer
      read(ny_sd, fdbuffer, sizeof(fdbuffer));
      
      // Hva havner i fdbuffer?
       //fprintf(stderr, "%s \n", fdbuffer);
      
      // Se gjennom GET-forespørselen og avgjør om det letes 
      // etter gyldig fil med gyldig filendelse. Hvis svaret er nei, skriv ut feilmelding
      char * test;
      char * saveptr = fdbuffer;
      test = strtok_r(fdbuffer, ".", &saveptr);
      //fprintf(stderr, "%p \n", &test);
      //printf("Linje106: %s \n", test);
      test = strtok_r(NULL, " ", &saveptr);
      //fprintf(stderr, "%p \n", &test);
      //printf("Linje109: %s \n", test);
      if(strcmp(test, "asis") == 0 || strcmp(test, "html") == 0 ||
      strcmp(test, "htm") == 0 || strcmp(test, "shtml") == 0 ||
      strcmp(test, "asc") == 0 || strcmp(test, "txt") == 0 ||
      strcmp(test, "text") == 0 || strcmp(test, "pot") == 0 ||
      strcmp(test, "brf") == 0 || strcmp(test, "srt") == 0 ||
      strcmp(test, "png") == 0 || strcmp(test, "svg") == 0 ||
      strcmp(test, "svgz") == 0 || strcmp(test, "xml") == 0 ||
      strcmp(test, "xsd") == 0 || strcmp(test, "xsl") == 0 ||
      strcmp(test, "xslt") == 0 || strcmp(test, "css") == 0 ||
      strcmp(test, "json") == 0){
		  /* Må avgjøre om filstien finnes 
		   * og kan aksesseres, ellers sendes feilmelding */
		  char dot[10]= ".";
		  char * test3 = NULL;
		  strtok_r(fdbuffer, " ", &saveptr);
		  //printf("Linje125: %s \n", test3);
		  test3 = strtok_r(NULL, " ", &saveptr);
		  //printf("Linje127: %s \n", test3);
		  strcat(dot, test);
		  strcat(test3, dot);
		  //printf("Linje130: %s \n", test3);
		  //fprintf(stderr, "Linje131: %s \n", test3);
		  if(access(test3, F_OK) == 0){
			  /* Vet nå at filsti er gyldig og at filtype er OK*/
			  
			  char * ptr;
			  // Skriver feilmelding dersom fil ikke skulle la seg åpne
			  /*if(fp == NULL){
				  fprintf(stderr, "The file '%p' failed to open \n", &fp);
				  }*/
			  if(strcmp(test, "asis") == 0 || strcmp(test, "asc") == 0 || strcmp(test, "txt") == 0 || strcmp(test, "text") == 0 || strcmp(test, "pot") == 0 || strcmp(test, "brf") == 0 || strcmp(test, "srt") == 0){
				  // Åpne fil
				  fp = fopen(test3, "r");
				  // Skrive HTTP head til socket
				  //ptr = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n";
				  //size_t st = strlen(ptr);
				  //write(ny_sd, ptr, st);
				  // Skrive filinnholdet til socket
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			 else if(strcmp(test, "html") == 0 || strcmp(test, "htm") == 0 || strcmp(test, "shtml") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			else if(strcmp(test, "png") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: image/png\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			else if(strcmp(test, "svg") == 0 || strcmp(test, "svgz") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: image/svg+xml\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			else if(strcmp(test, "xml") == 0 || strcmp(test, "xsd") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: application/xml\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			else if(strcmp(test, "xsl") == 0 || strcmp(test, "xsl") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: application/xslt+xml\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			else if(strcmp(test, "css") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: text/css\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
			else if(strcmp(test, "json") == 0){
				  fp = fopen(test3, "r");
				  ptr = "HTTP/1.1 200 OK\nContent-Type: application/json\n\n";
				  size_t st = strlen(ptr);
				  write(ny_sd, ptr, st);
				  while(fread(fbuffer, 1, 1024, fp) != 0)
					write(ny_sd, fbuffer, sizeof(fbuffer));
				  }
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
		// For å hindre zombie prosesser
		//signal(SIGCHLD, SIG_IGN);
		wait(NULL);
		
		// Steng fildeskriptor
      close(ny_sd);
      //printf("PID of parent process is %d\n", pid);
    }
  }
  return 0;
}

// Funksjon for demonisering av tjeneren
void demoniser(){
	pid_t ppid;
	//pid_t sid;
	ppid = fork();
	if(ppid != 0){
		exit(0); // Opphav gjør exit
	}
	/* Jobber nå på barnet som er blitt foreldreløs
	 * Kjører setsid() for å lage en ny sesjon der barneprosessen
	 * blir ny sesjonsleder og prosessgruppeleder uten kontrollterminal*/
	 setsid();
	 /*if(sid != -1)
		printf("The calling process with PID %d was not a process group leader", ppid);*/
		
	 // Ignorere SIGHUP når sesjonslederen i neste trinn skal termineres
	 signal(SIGHUP, SIG_IGN);
	 
	 /* Gjør fork på nytt for å hindre at tjeneren ikke lenger 
	  * er sesjonsleder og dermed ikke kan knytte seg til en
	  * kontrollterminal som er ledig */
	  if(fork() != 0){
		  exit(0); // Opphav gjør exit
	  }
	  
	  // Steng alle unødvendige filer
	  close(STDIN_FILENO);
	  close(STDOUT_FILENO);
	  //close(STDERR_FILENO);
		
}
/*printf("HTTP/1.1 200 OK\n");
      printf("Content-Type: text/plain\n");
      printf("\n");
      printf("HTTP/1.1 200 OK\nHei Anne-Marthe uwu!\nJeg synes data er goy!\n");
      */
