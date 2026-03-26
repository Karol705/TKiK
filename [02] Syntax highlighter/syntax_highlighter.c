#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

typedef enum {
    TOKEN_IDENTIFIER,
    TOKEN_NUMBER,
    TOKEN_FLOAT,
    TOKEN_STRING,
    TOKEN_CHAR,

    /* type keywords */
    TOKEN_INT,
    TOKEN_FLOAT_KW,
    TOKEN_CHAR_KW,
    TOKEN_VOID,

    /* control keywords */
    TOKEN_IF,
    TOKEN_ELSE,
    TOKEN_FOR,
    TOKEN_WHILE,
    TOKEN_RETURN,

    /* arithmetic */
    TOKEN_PLUS,        /* +  */
    TOKEN_MINUS,       /* -  */
    TOKEN_MULTIPLY,    /* *  */
    TOKEN_DIVIDE,      /* /  */
    TOKEN_MODULO,      /* %  */
    TOKEN_INCREMENT,   /* ++ */
    TOKEN_DECREMENT,   /* -- */

    /* relational / logical */
    TOKEN_ASSIGN,          /* =  */
    TOKEN_EQUAL,           /* == */
    TOKEN_NOT_EQUAL,       /* != */
    TOKEN_LESS,            /* <  */
    TOKEN_LESS_EQUAL,      /* <= */
    TOKEN_GREATER,         /* >  */
    TOKEN_GREATER_EQUAL,   /* >= */
    TOKEN_AND,             /* && */
    TOKEN_OR,              /* || */
    TOKEN_NOT,             /* !  */

    /* brackets */
    TOKEN_LPAREN,    /* ( */
    TOKEN_RPAREN,    /* ) */
    TOKEN_LBRACE,    /* { */
    TOKEN_RBRACE,    /* } */
    TOKEN_LBRACKET,  /* [ */
    TOKEN_RBRACKET,  /* ] */

    /* punctuation */
    TOKEN_SEMICOLON, /* ; */
    TOKEN_COMMA,     /* , */
    TOKEN_DOT,       /* . */
    TOKEN_COLON,     /* : */

    /* whole-line tokens */
    TOKEN_PREPROCESSOR,  /* #include …, #define …, etc. (full line) */
    TOKEN_COMMENT,       /* // … or /* … */  /* (full comment text)   */

    /* whitespace */
    TOKEN_SPACE,
    TOKEN_TAB,
    TOKEN_CR,
    TOKEN_EOL,

    TOKEN_EOF,
    TOKEN_UNKNOWN
} TokenType;


typedef struct {
    TokenType type;
    union {
        char* lexeme;
        int    number;
        double real;
    } value;
    int line;
    int column;
} Token;

typedef struct {
    FILE* file;
    int   currentChar;
    int   line;
    int   column;
} Scanner;


static char* scanLineCommentText(Scanner* s);
static char* scanBlockCommentText(Scanner* s);
static char* scanPreprocessorLine(Scanner* s);
static char* scanIdentifier(Scanner* s);

void initScanner(Scanner* s, FILE* file) {
    s->file = file;
    s->currentChar = fgetc(file);
    s->line = 1;
    s->column = 1;
}

static void advance(Scanner* s) {
    if (s->currentChar == '\n') {
        s->line++;
        s->column = 1;
    }
    else {
        s->column++;
    }
    s->currentChar = fgetc(s->file);
}

static Token makeTokenAt(TokenType type, int line, int col) {
    Token t;
    t.type = type;
    t.line = line;
    t.column = col;
    t.value.lexeme = NULL;
    return t;
}

static double scanNumberRaw(Scanner* s, int* isFloat) {
    long ipart = 0;
    *isFloat = 0;

    while (isdigit(s->currentChar)) {
        ipart = ipart * 10 + (s->currentChar - '0');
        advance(s);
    }

    double value = (double)ipart;

    if (s->currentChar == '.') {
        *isFloat = 1;
        advance(s);
        double factor = 0.1;
        while (isdigit(s->currentChar)) {
            value += (s->currentChar - '0') * factor;
            factor *= 0.1;
            advance(s);
        }
    }

    if (s->currentChar == 'e' || s->currentChar == 'E') {
        *isFloat = 1;
        advance(s);
        int sign = 1;
        if (s->currentChar == '+') { advance(s); }
        else if (s->currentChar == '-') { sign = -1; advance(s); }
        int exp = 0;
        while (isdigit(s->currentChar)) {
            exp = exp * 10 + (s->currentChar - '0');
            advance(s);
        }
        double mul = 1.0;
        for (int i = 0; i < exp; i++) mul *= 10.0;
        if (sign > 0) value *= mul; else value /= mul;
    }

    return value;
}

static char* scanIdentifier(Scanner* s) {
    char buffer[256];
    int  i = 0;

    while ((isalnum(s->currentChar) || s->currentChar == '_') && i < 255) {
        buffer[i++] = (char)s->currentChar;
        advance(s);
    }

    while (isalnum(s->currentChar) || s->currentChar == '_')
        advance(s);

    buffer[i] = '\0';
    return strdup(buffer);
}

static const struct { const char* kw; TokenType type; } keywords[] = {
    { "int",    TOKEN_INT      },
    { "float",  TOKEN_FLOAT_KW },
    { "char",   TOKEN_CHAR_KW  },
    { "void",   TOKEN_VOID     },
    { "if",     TOKEN_IF       },
    { "else",   TOKEN_ELSE     },
    { "for",    TOKEN_FOR      },
    { "while",  TOKEN_WHILE    },
    { "return", TOKEN_RETURN   },
};
#define NUM_KEYWORDS (int)(sizeof(keywords) / sizeof(keywords[0]))

static Token makeIdentifierOrKeywordToken(char* text, int line, int col) {
    Token token = makeTokenAt(TOKEN_IDENTIFIER, line, col);
    for (int i = 0; i < NUM_KEYWORDS; i++) {
        if (strcmp(text, keywords[i].kw) == 0) {
            token.type = keywords[i].type;
            free(text);
            return token;
        }
    }
    token.value.lexeme = text;
    return token;
}

static char resolveEscape(char c) {
    switch (c) {
    case 'n':  return '\n';
    case 't':  return '\t';
    case 'r':  return '\r';
    case '\\': return '\\';
    case '\'': return '\'';
    case '"':  return '"';
    case '0':  return '\0';
    default:   return c;
    }
}

static Token scanStringLiteral(Scanner* s, int line, int col) {
    advance(s);
    char buffer[4096];
    int  i = 0;

    while (s->currentChar != EOF && s->currentChar != '"') {
        char ch;
        if (s->currentChar == '\\') {
            advance(s);
            ch = resolveEscape((char)s->currentChar);
        }
        else {
            ch = (char)s->currentChar;
        }
        if (i < (int)sizeof(buffer) - 1) buffer[i++] = ch;
        advance(s);
    }
    if (s->currentChar == '"') advance(s);

    buffer[i] = '\0';
    Token t = makeTokenAt(TOKEN_STRING, line, col);
    t.value.lexeme = strdup(buffer);
    return t;
}

static Token scanCharLiteral(Scanner* s, int line, int col) {
    advance(s);
    char ch;
    if (s->currentChar == '\\') {
        advance(s);
        ch = resolveEscape((char)s->currentChar);
        advance(s);
    }
    else {
        ch = (char)s->currentChar;
        advance(s);
    }
    if (s->currentChar == '\'') advance(s);

    Token t = makeTokenAt(TOKEN_CHAR, line, col);
    char tmp[2] = { ch, '\0' };
    t.value.lexeme = strdup(tmp);
    return t;
}

static char* scanLineCommentText(Scanner* s) {
    char buffer[4096];
    int i = 0;
    buffer[i++] = '/'; buffer[i++] = '/';

    while (s->currentChar != '\n' && s->currentChar != EOF
        && i < (int)sizeof(buffer) - 1) {
        buffer[i++] = (char)s->currentChar;
        advance(s);
    }
    buffer[i] = '\0';
    return strdup(buffer);
}

static char* scanBlockCommentText(Scanner* s) {
    char buffer[8192];
    int i = 0;
    buffer[i++] = '/'; buffer[i++] = '*';

    while (s->currentChar != EOF) {
        if (s->currentChar == '*') {
            if (i < (int)sizeof(buffer) - 1) buffer[i++] = '*';
            advance(s);
            if (s->currentChar == '/') {
                if (i < (int)sizeof(buffer) - 1) buffer[i++] = '/';
                advance(s);
                break;
            }
        }
        else {
            if (i < (int)sizeof(buffer) - 1) buffer[i++] = (char)s->currentChar;
            advance(s);
        }
    }
    buffer[i] = '\0';
    return strdup(buffer);
}

static char* scanPreprocessorLine(Scanner* s) {
    char buffer[4096];
    int i = 0;
    buffer[i++] = '#';

    while (s->currentChar != '\n' && s->currentChar != EOF) {
        if (s->currentChar == '\\') {
            if (i < (int)sizeof(buffer) - 2) buffer[i++] = '\\';
            advance(s);
            if (s->currentChar == '\n') {
                if (i < (int)sizeof(buffer) - 2) buffer[i++] = '\n';
                advance(s);
                continue;
            }
        }
        if (i < (int)sizeof(buffer) - 1) buffer[i++] = (char)s->currentChar;
        advance(s);
    }
    buffer[i] = '\0';
    return strdup(buffer);
}

static void htmlEscape(const char* src, char* dst, int dstSize) {
    int j = 0;
    for (int i = 0; src[i] && j < dstSize - 7; i++) {
        switch ((unsigned char)src[i]) {
        case '<': memcpy(dst + j, "&lt;", 4); j += 4; break;
        case '>': memcpy(dst + j, "&gt;", 4); j += 4; break;
        case '&': memcpy(dst + j, "&amp;", 5); j += 5; break;
        case '"': memcpy(dst + j, "&quot;", 6); j += 6; break;
        case '\n': dst[j++] = '\n'; break;
        case '\t': memcpy(dst + j, "    ", 4); j += 4; break;  /* 4 spaces */
        default:   dst[j++] = src[i]; break;
        }
    }
    dst[j] = '\0';
}

static char htmlBuf[16384];
static char escBuf[12288];

static const char* tokenToHTML(const Token* token) {
    switch (token->type) {

        /* ---- numeric literals ---- */
    case TOKEN_NUMBER:
        sprintf(htmlBuf, "<span class=\"num\">%d</span>",
            token->value.number);
        return htmlBuf;

    case TOKEN_FLOAT:
        sprintf(htmlBuf, "<span class=\"num\">%g</span>",
            token->value.real);
        return htmlBuf;

        /* ---- string / char literals ---- */
    case TOKEN_STRING:
        htmlEscape(token->value.lexeme, escBuf, sizeof(escBuf));
        sprintf(htmlBuf, "<span class=\"str\">&quot;%s&quot;</span>",
            escBuf);
        return htmlBuf;

    case TOKEN_CHAR:
        htmlEscape(token->value.lexeme, escBuf, sizeof(escBuf));
        sprintf(htmlBuf, "<span class=\"str\">&#39;%s&#39;</span>",
            escBuf);
        return htmlBuf;

        /* ---- identifier ---- */
    case TOKEN_IDENTIFIER:
        htmlEscape(token->value.lexeme, escBuf, sizeof(escBuf));
        sprintf(htmlBuf, "<span class=\"id\">%s</span>", escBuf);
        return htmlBuf;

        /* ---- keywords ---- */
    case TOKEN_INT:      return "<span class=\"kw\">int</span>";
    case TOKEN_FLOAT_KW: return "<span class=\"kw\">float</span>";
    case TOKEN_CHAR_KW:  return "<span class=\"kw\">char</span>";
    case TOKEN_VOID:     return "<span class=\"kw\">void</span>";
    case TOKEN_IF:       return "<span class=\"kw\">if</span>";
    case TOKEN_ELSE:     return "<span class=\"kw\">else</span>";
    case TOKEN_FOR:      return "<span class=\"kw\">for</span>";
    case TOKEN_WHILE:    return "<span class=\"kw\">while</span>";
    case TOKEN_RETURN:   return "<span class=\"kw\">return</span>";

        /* ---- preprocessor directive (whole line) ---- */
    case TOKEN_PREPROCESSOR:
        htmlEscape(token->value.lexeme, escBuf, sizeof(escBuf));
        sprintf(htmlBuf, "<span class=\"pp\">%s</span>", escBuf);
        return htmlBuf;

        /* ---- comment (whole comment text) ---- */
    case TOKEN_COMMENT:
        htmlEscape(token->value.lexeme, escBuf, sizeof(escBuf));
        sprintf(htmlBuf, "<span class=\"cmt\">%s</span>", escBuf);
        return htmlBuf;

        /* ---- arithmetic operators ---- */
    case TOKEN_PLUS:      return "<span class=\"op\">+</span>";
    case TOKEN_MINUS:     return "<span class=\"op\">-</span>";
    case TOKEN_MULTIPLY:  return "<span class=\"op\">*</span>";
    case TOKEN_DIVIDE:    return "<span class=\"op\">/</span>";
    case TOKEN_MODULO:    return "<span class=\"op\">%</span>";
    case TOKEN_INCREMENT: return "<span class=\"op\">++</span>";
    case TOKEN_DECREMENT: return "<span class=\"op\">--</span>";

        /* ---- relational / logical operators ---- */
    case TOKEN_ASSIGN:        return "<span class=\"op\">=</span>";
    case TOKEN_EQUAL:         return "<span class=\"op\">==</span>";
    case TOKEN_NOT_EQUAL:     return "<span class=\"op\">!=</span>";
    case TOKEN_LESS:          return "<span class=\"op\">&lt;</span>";
    case TOKEN_LESS_EQUAL:    return "<span class=\"op\">&lt;=</span>";
    case TOKEN_GREATER:       return "<span class=\"op\">&gt;</span>";
    case TOKEN_GREATER_EQUAL: return "<span class=\"op\">&gt;=</span>";
    case TOKEN_AND:           return "<span class=\"op\">&amp;&amp;</span>";
    case TOKEN_OR:            return "<span class=\"op\">||</span>";
    case TOKEN_NOT:           return "<span class=\"op\">!</span>";

        /* ---- brackets ---- */
    case TOKEN_LPAREN:   return "<span class=\"br\">(</span>";
    case TOKEN_RPAREN:   return "<span class=\"br\">)</span>";
    case TOKEN_LBRACE:   return "<span class=\"br\">{</span>";
    case TOKEN_RBRACE:   return "<span class=\"br\">}</span>";
    case TOKEN_LBRACKET: return "<span class=\"br\">[</span>";
    case TOKEN_RBRACKET: return "<span class=\"br\">]</span>";

        /* ---- punctuation ---- */
    case TOKEN_SEMICOLON: return "<span class=\"punct\">;</span>";
    case TOKEN_COMMA:     return "<span class=\"punct\">,</span>";
    case TOKEN_DOT:       return "<span class=\"punct\">.</span>";
    case TOKEN_COLON:     return "<span class=\"punct\">:</span>";

        /* ---- whitespace ---- */
    case TOKEN_SPACE: return " ";
    case TOKEN_TAB:   return "    ";   /* four spaces inside <pre> */
    case TOKEN_CR:    return "";       /* swallow bare \r           */
    case TOKEN_EOL:   return "\n";

        /* ---- end / unknown ---- */
    case TOKEN_EOF: return "";

    default:
        /* Emit the unknown character safely */
        if (token->value.lexeme) {
            htmlEscape(token->value.lexeme, escBuf, sizeof(escBuf));
            sprintf(htmlBuf, "<span class=\"unk\">%s</span>", escBuf);
            return htmlBuf;
        }
        return "<span class=\"unk\">?</span>";
    }
}

Token getNextToken(Scanner* s) {
    int line = s->line;
    int col = s->column;

    if (s->currentChar == EOF)
        return makeTokenAt(TOKEN_EOF, line, col);

    /* ---- whitespace (emitted as individual tokens to preserve layout) ---- */
    if (s->currentChar == ' ') { advance(s); return makeTokenAt(TOKEN_SPACE, line, col); }
    if (s->currentChar == '\t') { advance(s); return makeTokenAt(TOKEN_TAB, line, col); }
    if (s->currentChar == '\r') { advance(s); return makeTokenAt(TOKEN_CR, line, col); }
    if (s->currentChar == '\n') { advance(s); return makeTokenAt(TOKEN_EOL, line, col); }

    /* ---- numeric literals ---- */
    if (isdigit(s->currentChar)) {
        int    isFloat;
        double raw = scanNumberRaw(s, &isFloat);
        Token  t = makeTokenAt(isFloat ? TOKEN_FLOAT : TOKEN_NUMBER, line, col);
        if (isFloat) t.value.real = raw;
        else         t.value.number = (int)raw;
        return t;
    }

    /* ---- identifiers and keywords ---- */
    if (isalpha(s->currentChar) || s->currentChar == '_')
        return makeIdentifierOrKeywordToken(scanIdentifier(s), line, col);

    /* ---- string / char literals ---- */
    if (s->currentChar == '"')  return scanStringLiteral(s, line, col);
    if (s->currentChar == '\'') return scanCharLiteral(s, line, col);

    /* ---- operators and punctuation ---- */
    switch (s->currentChar) {

    case '+':
        advance(s);
        if (s->currentChar == '+') { advance(s); return makeTokenAt(TOKEN_INCREMENT, line, col); }
        return makeTokenAt(TOKEN_PLUS, line, col);

    case '-':
        advance(s);
        if (s->currentChar == '-') { advance(s); return makeTokenAt(TOKEN_DECREMENT, line, col); }
        return makeTokenAt(TOKEN_MINUS, line, col);

    case '*':
        advance(s);
        return makeTokenAt(TOKEN_MULTIPLY, line, col);

    case '/':
        advance(s);
        if (s->currentChar == '/') {
            /* line comment — preserve and colour */
            advance(s);
            Token t = makeTokenAt(TOKEN_COMMENT, line, col);
            t.value.lexeme = scanLineCommentText(s);
            return t;
        }
        if (s->currentChar == '*') {
            /* block comment — preserve and colour */
            advance(s);
            Token t = makeTokenAt(TOKEN_COMMENT, line, col);
            t.value.lexeme = scanBlockCommentText(s);
            return t;
        }
        return makeTokenAt(TOKEN_DIVIDE, line, col);

    case '#':
        /* scan the entire preprocessor directive as one token */
        advance(s);
        {
            Token t = makeTokenAt(TOKEN_PREPROCESSOR, line, col);
            t.value.lexeme = scanPreprocessorLine(s);
            return t;
        }

    case '%': advance(s); return makeTokenAt(TOKEN_MODULO, line, col);

    case '&':
        advance(s);
        if (s->currentChar == '&') { advance(s); return makeTokenAt(TOKEN_AND, line, col); }
        return makeTokenAt(TOKEN_UNKNOWN, line, col);

    case '|':
        advance(s);
        if (s->currentChar == '|') { advance(s); return makeTokenAt(TOKEN_OR, line, col); }
        return makeTokenAt(TOKEN_UNKNOWN, line, col);

    case '=':
        advance(s);
        if (s->currentChar == '=') { advance(s); return makeTokenAt(TOKEN_EQUAL, line, col); }
        return makeTokenAt(TOKEN_ASSIGN, line, col);

    case '!':
        advance(s);
        if (s->currentChar == '=') { advance(s); return makeTokenAt(TOKEN_NOT_EQUAL, line, col); }
        return makeTokenAt(TOKEN_NOT, line, col);

    case '<':
        advance(s);
        if (s->currentChar == '=') { advance(s); return makeTokenAt(TOKEN_LESS_EQUAL, line, col); }
        return makeTokenAt(TOKEN_LESS, line, col);

    case '>':
        advance(s);
        if (s->currentChar == '=') { advance(s); return makeTokenAt(TOKEN_GREATER_EQUAL, line, col); }
        return makeTokenAt(TOKEN_GREATER, line, col);

    case '(':  advance(s); return makeTokenAt(TOKEN_LPAREN, line, col);
    case ')':  advance(s); return makeTokenAt(TOKEN_RPAREN, line, col);
    case '{':  advance(s); return makeTokenAt(TOKEN_LBRACE, line, col);
    case '}':  advance(s); return makeTokenAt(TOKEN_RBRACE, line, col);
    case '[':  advance(s); return makeTokenAt(TOKEN_LBRACKET, line, col);
    case ']':  advance(s); return makeTokenAt(TOKEN_RBRACKET, line, col);
    case ';':  advance(s); return makeTokenAt(TOKEN_SEMICOLON, line, col);
    case ',':  advance(s); return makeTokenAt(TOKEN_COMMA, line, col);
    case '.':  advance(s); return makeTokenAt(TOKEN_DOT, line, col);
    case ':':  advance(s); return makeTokenAt(TOKEN_COLON, line, col);
    }

    /* ---- truly unknown character ---- */
    {
        char unk = (char)s->currentChar;
        fprintf(stderr, "Unknown character '%c' (0x%02x) at %d:%d\n",
            unk, (unsigned char)unk, s->line, s->column);
        advance(s);
        Token t = makeTokenAt(TOKEN_UNKNOWN, line, col);
        char tmp[2] = { unk, '\0' };
        t.value.lexeme = strdup(tmp);
        return t;
    }
}

static const char HTML_HEADER[] =
"<!DOCTYPE html>\n"
"<html>\n"
"<head>\n"
"  <meta charset=\"UTF-8\">\n"
"  <title>Syntax Highlighted C</title>\n"
"  <style>\n"
"    body  { background: #1e1e1e; margin: 0; padding: 1.5rem; }\n"
"    pre   {\n"
"      font-family: Consolas, 'Courier New', monospace;\n"
"      font-size: 14px;\n"
"      line-height: 1.5;\n"
"      color: #d4d4d4;\n"
"      background: #1e1e1e;\n"
"      margin: 0;\n"
"    }\n"
"    .kw   { color: #569cd6; }   /* keywords              */\n"
"    .pp   { color: #c586c0; }   /* preprocessor          */\n"
"    .cmt  { color: #6a9955; }   /* comments              */\n"
"    .str  { color: #ce9178; }   /* string/char literals  */\n"
"    .num  { color: #b5cea8; }   /* numeric literals      */\n"
"    .id   { color: #9cdcfe; }   /* identifiers           */\n"
"    .op   { color: #d4d4d4; }   /* operators             */\n"
"    .br   { color: #ffd700; }   /* brackets              */\n"
"    .punct{ color: #d4d4d4; }   /* punctuation           */\n"
"    .unk  { color: #f44747; }   /* unknown characters    */\n"
"  </style>\n"
"</head>\n"
"<body><pre>\n";

static const char HTML_FOOTER[] = "</pre></body></html>\n";

int main(int argc, char* argv[]) {
    const char* inName = argc > 1 ? argv[1] : "file.txt";
    FILE* fin = fopen(inName, "r");
    if (!fin) {
        fprintf(stderr, "Error: cannot open '%s'\n", inName);
        return 1;
    }

    const char* outName = argc > 2 ? argv[2] : "output.html";
    FILE* fout = stdout;
    fout = fopen(outName, "w");
    if (!fout) {
        fprintf(stderr, "Error: cannot create '%s'\n", outName);
        fclose(fin);
        return 1;
    }


    Scanner scanner;
    initScanner(&scanner, fin);

    fputs(HTML_HEADER, fout);

    while (1) {
        Token token = getNextToken(&scanner);

        /* emit the coloured HTML for this token */
        fputs(tokenToHTML(&token), fout);

        /* free any heap-allocated lexeme */
        switch (token.type) {
        case TOKEN_IDENTIFIER:
        case TOKEN_STRING:
        case TOKEN_CHAR:
        case TOKEN_COMMENT:
        case TOKEN_PREPROCESSOR:
        case TOKEN_UNKNOWN:
            free(token.value.lexeme);
            break;
        default:
            break;
        }

        if (token.type == TOKEN_EOF) break;
    }

    fputs(HTML_FOOTER, fout);

    fclose(fin);
    if (fout != stdout) {
        fclose(fout);
        printf("Output written to '%s'\n", outName);
    }
    return 0;
}
