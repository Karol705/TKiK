#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

typedef enum {
    TOKEN_NUMBER,
    TOKEN_PLUS,        // +
    TOKEN_MINUS,       // -
    TOKEN_MULTIPLY,    // *
    TOKEN_DIVIDE,      // /
    TOKEN_LPAREN,      // (
    TOKEN_RPAREN,      // )
    TOKEN_EOF
} TokenType;

typedef struct {
    TokenType type;

    union {
        char* string;   // for identifiers, keywords, strings
        int number;     // for integer literals
        double real;    // for floating-point numbers
    } value;

    int line;
    int column;
} Token;

typedef struct {
    FILE* file;
    int currentChar;
    int line;
    int column;
} Scanner;

void initScanner(Scanner* s, FILE* file) {
    s->file = file;
    s->currentChar = fgetc(file);
    s->line = 1;
    s->column = 1;
}

void advance(Scanner* s) {
    if (s->currentChar == '\n') {
        s->line++;
        s->column = 1;
    }
    else {
        s->column++;
    }

    s->currentChar = fgetc(s->file);
}

void skipWhiteSpace(Scanner* s) {
    while (s->currentChar == ' ' ||
        s->currentChar == '\t' ||
        s->currentChar == '\n') {
        advance(s);
    }
}

int scanNumber(Scanner* s) {
    int value = 0;

    while (isdigit(s->currentChar)) {
        value = value * 10 + (s->currentChar - '0');
        advance(s);
    }

    return value;
}

Token makeToken(TokenType type, Scanner* s) {
    Token token;
    token.type = type;
    token.line = s->line;
    token.column = s->column;
    return token;
}
Token makeNumberToken(int value, Scanner* s) {
    Token token = makeToken(TOKEN_NUMBER, s);
    token.value.number = value;
    return token;
}

const char* tokenToString(Token token) {
    static char buffer[50];
    switch (token.type) {
    case TOKEN_NUMBER:
        sprintf(buffer, "NUMBER(%d)", token.value.number);
        return buffer;
    case TOKEN_PLUS:
        return "PLUS";
    case TOKEN_MINUS:
        return "MINUS";
    case TOKEN_MULTIPLY:
        return "MULTIPLY";
    case TOKEN_DIVIDE:
        return "DIVIDE";
    case TOKEN_LPAREN:
        return "LPAREN";
    case TOKEN_RPAREN:
        return "RPAREN";
    case TOKEN_EOF:
        return "EOF";
    default:
        return "UNKNOWN";
    }
}

Token getNextToken(Scanner* s) {
    skipWhiteSpace(s);

    if (s->currentChar == EOF)
        return makeToken(TOKEN_EOF, s);

    if (isdigit(s->currentChar)) {
        int value = scanNumber(s);
        return makeNumberToken(value, s);
    }

    if (s->currentChar == '+') {
        advance(s);
        return makeToken(TOKEN_PLUS, s);
    }

    if (s->currentChar == '-') {
        advance(s);
        return makeToken(TOKEN_MINUS, s);
    }

    if (s->currentChar == '*') {
        advance(s);
        return makeToken(TOKEN_MULTIPLY, s);
    }

    if (s->currentChar == '/') {
        advance(s);
        return makeToken(TOKEN_DIVIDE, s);
    }

    if (s->currentChar == '(') {
        advance(s);
        return makeToken(TOKEN_LPAREN, s);
    }

    if (s->currentChar == ')') {
        advance(s);
        return makeToken(TOKEN_RPAREN, s);
    }


    perror("Unknown character");
}

int main(int argc, char* argv[]) {
    const char* input = argc > 1 ? argv[1] : "input.txt";
    const char* output = argc > 2 ? argv[2] : "output.txt";

    Scanner scanner;
    FILE* file_in = fopen(input, "r");
    FILE* file_out = fopen(output, "w");
    initScanner(&scanner, file_in);

    while (1) {
        Token token = getNextToken(&scanner);
        // printf("Token: %s (line %d, column %d)\n", tokenToString(token), token.line, token.column);
        fprintf(file_out, "Token: %s (line %d, column %d)\n", tokenToString(token), token.line, token.column);
        if (token.type == TOKEN_EOF)
            break;
    }
    fclose(file_in);
    fclose(file_out);

    return 0;
}