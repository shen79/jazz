#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#define on_error(...) { fprintf(stderr, __VA_ARGS__); fflush(stderr); }
/*
	source: https://raw.githubusercontent.com/mafintosh/echo-servers.c/master/tcp-echo-server.c
*/


void handle_client_input(int client_fd) {
	int err;
	char buf[1024];
	int read = recv(client_fd, buf, 2048, 0);
	if (!read) return;
	if (read < 0) on_error("Client read failed\n");
	err = send(client_fd, buf, read, 0);
	if (err < 0) on_error("Client write failed\n");
}

void handle_client(int server_fd) {
	struct sockaddr_in client;
	int client_fd;

	socklen_t client_len = sizeof(client);
	client_fd = accept(server_fd, (struct sockaddr *) &client, &client_len);

	if (client_fd < 0) on_error("Could not establish new connection\n");
	handle_client_input(client_fd);
}

int main (int argc, char *argv[]) {
  int server_fd, err;
  struct sockaddr_in server;

  if (argc < 2) on_error("Usage: %s [port]\n", argv[0]);
  int port = atoi(argv[1]);

  server_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (server_fd < 0) on_error("Could not create socket\n");

  server.sin_family = AF_INET;
  server.sin_port = htons(port);
  server.sin_addr.s_addr = htonl(INADDR_ANY);

  int opt_val = 1;
  setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt_val, sizeof opt_val);

  err = bind(server_fd, (struct sockaddr *) &server, sizeof(server));
  if (err < 0) on_error("Could not bind socket\n");

  err = listen(server_fd, 128);
  if (err < 0) on_error("Could not listen on socket\n");

  printf("Server is listening on %d\n", port);
//  while (1) {
  handle_client(server_fd);
//  }

  return 0;
}
