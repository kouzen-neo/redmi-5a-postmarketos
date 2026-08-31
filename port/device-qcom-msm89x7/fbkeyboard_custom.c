/*
 * fbkeyboard.c : framebuffer softkeyboard for touchscreen devices
 * Customized for Xiaomi Redmi 5A (postmarketOS)
 * - Cyberpunk Neon Green Matrix Theme (0x00ff00)
 * - Top Row: :  /  <  >  v  ^  -
 * - Bottom Row: 123!@" | Ctrl | Space | . | Alt | Enter
 * - Precise touch index mapping without collisions
 */

#include <stdlib.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <errno.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <linux/vt.h>
#include <ft2build.h>
#include FT_FREETYPE_H

volatile sig_atomic_t done = 0;

char *font = "/usr/share/fonts/dejavu/DejaVuSans.ttf";
char *device = NULL;

char *special[][7] = {
	{ " : ", " / ", " < ", " > ", " v ", " ^ ", " - " },
	{ " ~ ", " ? ", "Home", "End", "PgDn", "PgUp", " _ " },
};

char *layout[] = {
	"qwertyuiopasdfghjklzxcvbnm",
	"QWERTYUIOPASDFGHJKLZXCVBNM",
	"1234567890-=[];\'\\,.`/     ",
	"!@#$%^&*()_+{}:\"|<>~?     "
};

int layoutuse = 0;
int ctrllock = 0;
int altlock = 0;
__u16 keys[][26] = {
	{ KEY_SEMICOLON, KEY_SLASH, KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP, KEY_MINUS },
	{ KEY_Q, KEY_W, KEY_E, KEY_R, KEY_T, KEY_Y, KEY_U, KEY_I, KEY_O, KEY_P,
	  KEY_A, KEY_S, KEY_D, KEY_F, KEY_G, KEY_H, KEY_J, KEY_K, KEY_L,
	  KEY_Z, KEY_X, KEY_C, KEY_V, KEY_B, KEY_N, KEY_M },
	{ KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0,
	  KEY_MINUS, KEY_EQUAL, KEY_LEFTBRACE, KEY_RIGHTBRACE, KEY_SEMICOLON, KEY_APOSTROPHE, KEY_BACKSLASH, KEY_COMMA, KEY_DOT,
	  KEY_GRAVE, KEY_SLASH, KEY_C, KEY_V, KEY_B, KEY_N, KEY_M },
	{ KEY_LEFTSHIFT, KEY_BACKSPACE },
	{ KEY_LEFTCTRL, KEY_SPACE, KEY_DOT, KEY_LEFTALT, KEY_ENTER },
	{ KEY_HOME, KEY_UP, KEY_PAGEUP,
	  KEY_LEFT, KEY_ENTER, KEY_RIGHT,
	  KEY_END, KEY_DOWN, KEY_PAGEDOWN,
	  KEY_RIGHTSHIFT }
};

#define TOUCHCOLOR 0x00ff00
#define BUTTONCOLOR 0x000000
#define BACKLITCOLOR 0x00ff00
#define TERMCOLOR 0x000000
int gap = 2;

int rotate = 0;

struct fb_var_screeninfo vinfo;
struct fb_fix_screeninfo finfo;
char *buf;
unsigned int buflen;
int fbheight;
int fbwidth;
int fblinelength;
int height;
int width;
int linelength;
int landscape;

FT_Face face;
int advance;

int fduinput;
struct input_event ie;
int theight;
int twidth;
int trowh;

void fill_rect(int x, int y, int w, int h, int color)
{
	int i, j;
	int32_t *line;
	if (x < 0) { w += x; x = 0; }
	if (y < 0) { h += y; y = 0; }
	if (w <= 0 || h <= 0) return;
	if (x + w > width) w = width - x;
	if (y + h > height * 5) h = height * 5 - y;

	switch (rotate) {
		case FB_ROTATE_UR:
			line = (int32_t *) (buf + y * linelength + x * 4);
			for (i = 0; i < h; i++) {
				for (j = 0; j < w; j++)
					line[j] = color;
				line += linelength / 4;
			}
			break;
		case FB_ROTATE_UD:
			line = (int32_t *) (buf +
					    (height * 5 - y -
					     1) * linelength + (width - x -
								1) * 4);
			for (i = 0; i < h; i++) {
				for (j = 0; j < w; j++)
					line[-j] = color;
				line -= linelength / 4;
			}
			break;
		case FB_ROTATE_CW:
			line = (int32_t *) (buf + x * linelength +
					    (width - y - 1) * 4);
			for (i = 0; i < h; i++) {
				for (j = 0; j < w; j++)
					line[j * linelength / 4] = color;
				line--;
			}
			break;
		case FB_ROTATE_CCW:
			line = (int32_t *) (buf +
					    (height * 5 - x - 1) * linelength +
					    y * 4);
			for (i = 0; i < h; i++) {
				for (j = 0; j < w; j++)
					line[-j * linelength / 4] = color;
				line++;
			}
			break;
	}
}

void draw_glyph(FT_Bitmap *bitmap, int x, int y)
{
	int i, j, p, q;
	int x_max;
	int y_max;
	int32_t *line;

	if (!bitmap || !bitmap->buffer || bitmap->width <= 0 || bitmap->rows <= 0)
		return;

	x_max = x + bitmap->width;
	y_max = y + bitmap->rows;

	for (i = x, p = 0; i < x_max; i++, p++) {
		for (j = y, q = 0; j < y_max; j++, q++) {
			if (i < 0 || j < 0 || i >= width || j >= height * 5)
				continue;
			if (bitmap->buffer[q * bitmap->width + p] > 128) {
				switch (rotate) {
					case FB_ROTATE_UR:
						line = (int32_t *) (buf +
								    j *
								    linelength +
								    i * 4);
						*line = BACKLITCOLOR;
						break;
					case FB_ROTATE_UD:
						line = (int32_t *) (buf +
								    (height *
								     5 - j -
								     1) *
								    linelength +
								    (width - i -
								     1) * 4);
						*line = BACKLITCOLOR;
						break;
					case FB_ROTATE_CW:
						line = (int32_t *) (buf +
								    i *
								    linelength +
								    (width - j -
								     1) * 4);
						*line = BACKLITCOLOR;
						break;
					case FB_ROTATE_CCW:
						line = (int32_t *) (buf +
								    (height *
								     5 - i -
								     1) *
								    linelength +
								    j * 4);
						*line = BACKLITCOLOR;
						break;
				}
			}
		}
	}
}

void draw_char(int x, int y, int character)
{
	if (character == ' ' || character == 0) {
		advance = height * 1 / 4;
		return;
	}
	if (FT_Load_Char(face, character, FT_LOAD_RENDER))
		return;
	draw_glyph(&face->glyph->bitmap, x + face->glyph->bitmap_left,
		   y - face->glyph->bitmap_top);
	advance = face->glyph->advance.x >> 6;
}

void draw_text(int x, int y, char *text)
{
	if (!text) return;
	while (*text) {
		draw_char(x, y, *text);
		x += advance;
		text++;
	}
}

void draw_key(int x, int y, int w, int h, int color)
{
	fill_rect(x + gap, y + gap, w - 2 * gap, 1, BACKLITCOLOR);
	fill_rect(x + gap, y + h - gap, w - 2 * gap, 1, BACKLITCOLOR);
	fill_rect(x + gap, y + gap, 1, h - 2 * gap, BACKLITCOLOR);
	fill_rect(x + w - gap, y + gap, 1, h - 2 * gap, BACKLITCOLOR);
	fill_rect(x + gap + 1, y + gap + 1, w - 2 * gap - 2,
		  h - 2 * gap - 2, color);
}

void draw_textbutton(int x, int y, int w, int h, int color, char *text)
{
	int l;
	if (!text) return;
	l = strlen(text);
	draw_key(x, y, w, h, color);
	draw_text(x + w / 2 - l * height * 1 / 10, y + height * 2 / 3, text);
}

void draw_button(int x, int y, int w, int h, int color, int character)
{
	draw_key(x, y, w, h, color);
	draw_char(x + w / 2 - height * 1 / 10, y + height * 2 / 3, character);
}

void draw_keyboard(int row, int pressed)
{
	int key;
	// Row 0 (Special top bar: : / < > v ^ -)
	for (key = 0; key < 7; key++) {
		draw_textbutton(key * width / 7 + 1, 1,
				width / 7 - 1, height - 1,
				(row == 0 && key == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
				special[layoutuse & 1][key]);
	}
	// Row 1 (q - p)
	for (key = 0; key < 10; key++) {
		draw_button(key * width / 10 + 1, height * 1,
			    width / 10 - 1, height - 1,
			    (row == 1 && key == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			    layout[layoutuse][key]);
	}
	// Row 2 (a - l)
	for (key = 0; key < 9; key++) {
		draw_button(key * width / 10 + width / 20 + 1, height * 2,
			    width / 10 - 1, height - 1,
			    (row == 1 && (key + 10) == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			    layout[layoutuse][key + 10]);
	}
	// Row 3 (Shift, z - m, Bcksp)
	draw_textbutton(1, height * 3, width * 3 / 20 - 1, height - 1,
			(layoutuse & 1) ? TOUCHCOLOR : BUTTONCOLOR,
			"Shift");
	for (key = 0; key < 7; key++) {
		draw_button(key * width / 10 + width * 3 / 20 + 1, height * 3,
			    width / 10 - 1, height - 1,
			    (row == 1 && (key + 19) == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			    layout[layoutuse][key + 19]);
	}
	draw_textbutton(width * 17 / 20, height * 3,
			width * 3 / 20 - 1, height - 1,
			(row == 3 && 1 == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			"Bcksp");

	// Row 4 (Bottom Bar: 123!@" | Ctrl | Space | . | Alt | Enter)
	draw_textbutton(1, height * 4, width * 3 / 20 - 1,
			height - 1,
			(99 == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			(layoutuse & 2) ? "abcABC" : "123!@\"");
	
	// Ctrl di kiri (setelah 123!@")
	draw_textbutton(width * 3 / 20, height * 4,
			width / 10 - 1, height - 1,
			(ctrllock || (row == 4 && 0 == pressed)) ? TOUCHCOLOR : BUTTONCOLOR,
			"Ctrl");
	
	// Spacebar (diperkecil jadi 40% lebar layar)
	draw_button(width * 5 / 20, height * 4, width * 8 / 20 - 1,
		    height - 1, (row == 4 && 1 == pressed) ? TOUCHCOLOR : BUTTONCOLOR, ' ');
	
	// Tombol Titik '.' di samping kiri Alt
	draw_textbutton(width * 13 / 20, height * 4,
			width / 10 - 1, height - 1,
			(row == 4 && 2 == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			" . ");
	
	// Alt di kanan (sebelum Enter)
	draw_textbutton(width * 15 / 20, height * 4,
			width / 10 - 1, height - 1,
			(altlock || (row == 4 && 3 == pressed)) ? TOUCHCOLOR : BUTTONCOLOR,
			"Alt");
	
	// Enter di ujung kanan
	draw_textbutton(width * 17 / 20, height * 4,
			width * 3 / 20 - 1, height - 1,
			(row == 4 && 4 == pressed) ? TOUCHCOLOR : BUTTONCOLOR,
			"Enter");
}

void show_fbkeyboard(int fbfd)
{
	switch (rotate) {
		case FB_ROTATE_UR:
			lseek(fbfd, fblinelength * (fbheight - height * 5), SEEK_SET);
			write(fbfd, buf, buflen);
			break;
		case FB_ROTATE_UD:
			lseek(fbfd, 0, SEEK_SET);
			write(fbfd, buf, buflen);
			break;
		case FB_ROTATE_CW:
			lseek(fbfd, 0, SEEK_SET);
			write(fbfd, buf, buflen);
			break;
		case FB_ROTATE_CCW:
			lseek(fbfd, fblinelength * (fbwidth - height * 5), SEEK_SET);
			write(fbfd, buf, buflen);
			break;
	}
}

void identify_touched_key(int x, int y, int *row, int *pressed)
{
	switch ((0x10000 - y) / trowh) {
		case 4:
			*row = 0;		// Row 0: Special top bar
			*pressed = x * 7 / 0x10000;
			break;
		case 3:
			*row = 1;		// Row 1: q - p (0..9)
			*pressed = x * 10 / 0x10000;
			break;
		case 2:
			*row = 1;		// Row 2: a - l (10..18)
			if (x > 0x10000 / 20 && x < 0x10000 * 19 / 20)
				*pressed = 10 + (x * 10 - 0x10000 / 2) / 0x10000;
			break;
		case 1:
			if (x < 0x10000 * 3 / 20) {
				*row = 3;
				*pressed = 0;	// Left Shift
			} else if (x < 0x10000 * 17 / 20) {
				*row = 1;	// Row 3 letters: z - m (19..25)
				*pressed = 19 + (x * 10 - 0x10000 * 3 / 2) / 0x10000;
			} else {
				*row = 3;
				*pressed = 1;	// Bcksp
			}
			break;
		case 0:
			*row = 4;
			if (x < 0x10000 * 3 / 20)
				*pressed = 99;	// 123!@"
			else if (x < 0x10000 * 5 / 20)
				*pressed = 0;	// Left Ctrl (Swapped)
			else if (x < 0x10000 * 13 / 20)
				*pressed = 1;	// Space
			else if (x < 0x10000 * 15 / 20)
				*pressed = 2;	// Dot '.'
			else if (x < 0x10000 * 17 / 20)
				*pressed = 3;	// Right Alt (Swapped)
			else
				*pressed = 4;	// Enter
			break;
		default:
			*row = 5;
			*pressed = 3 * y / (0x10000 - trowh * 5);
			*pressed *= 3;
			*pressed += 3 * x / 0x10000;
			break;
	}
}

void send_key(__u16 code)
{
	ie.type = EV_KEY;
	ie.code = code;
	ie.value = 1;
	if (write(fduinput, &ie, sizeof(ie)) != sizeof(ie))
		fprintf(stderr, "error: sending uinput event\n");
	ie.value = 0;
	if (write(fduinput, &ie, sizeof(ie)) != sizeof(ie))
		fprintf(stderr, "error: sending uinput event\n");
	ie.type = EV_SYN;
	ie.code = SYN_REPORT;
	if (write(fduinput, &ie, sizeof(ie)) != sizeof(ie))
		fprintf(stderr, "error: sending uinput event\n");
}

void send_shifted_key(__u16 code)
{
	struct input_event ev;
	memset(&ev, 0, sizeof(ev));
	
	// Shift down
	ev.type = EV_KEY; ev.code = KEY_LEFTSHIFT; ev.value = 1;
	write(fduinput, &ev, sizeof(ev));
	ev.type = EV_SYN; ev.code = SYN_REPORT; ev.value = 0;
	write(fduinput, &ev, sizeof(ev));

	// Key press
	ev.type = EV_KEY; ev.code = code; ev.value = 1;
	write(fduinput, &ev, sizeof(ev));
	ev.value = 0;
	write(fduinput, &ev, sizeof(ev));
	ev.type = EV_SYN; ev.code = SYN_REPORT; ev.value = 0;
	write(fduinput, &ev, sizeof(ev));

	// Shift up
	ev.type = EV_KEY; ev.code = KEY_LEFTSHIFT; ev.value = 0;
	write(fduinput, &ev, sizeof(ev));
	ev.type = EV_SYN; ev.code = SYN_REPORT; ev.value = 0;
	write(fduinput, &ev, sizeof(ev));
}

void send_uinput_event(int row, int pressed)
{
	if (pressed == 99) {
		layoutuse ^= 2;
	} else if (row == 0) {
		// Top row: :  /  <  >  v  ^  -
		if ((layoutuse & 1) == 0) {
			switch (pressed) {
				case 0: send_shifted_key(KEY_SEMICOLON); break; // : (Colon)
				case 1: send_key(KEY_SLASH); break;             // / (Slash)
				case 2: send_key(KEY_LEFT); break;              // < (Left Arrow)
				case 3: send_key(KEY_RIGHT); break;             // > (Right Arrow)
				case 4: send_key(KEY_DOWN); break;              // v (Down Arrow)
				case 5: send_key(KEY_UP); break;                // ^ (Up Arrow)
				case 6: send_key(KEY_MINUS); break;             // - (Minus)
			}
		} else {
			// Shifted top row: ~  ?  Home End PgDn PgUp _
			switch (pressed) {
				case 0: send_shifted_key(KEY_GRAVE); break;     // ~ (Tilde)
				case 1: send_shifted_key(KEY_SLASH); break;     // ? (Question mark)
				case 2: send_key(KEY_HOME); break;              // Home
				case 3: send_key(KEY_END); break;               // End
				case 4: send_key(KEY_PAGEDOWN); break;          // PgDn
				case 5: send_key(KEY_PAGEUP); break;            // PgUp
				case 6: send_shifted_key(KEY_MINUS); break;     // _ (Underscore)
			}
		}
	} else if (row == 1) {
		// Normal keys (q-p, a-l, z-m) across layout
		send_key(keys[row + (layoutuse >> 1)][pressed]);
	} else if (row == 3 && pressed == 0) {
		// Left Shift
		layoutuse ^= 1;
		ie.type = EV_KEY;
		ie.code = KEY_LEFTSHIFT;
		ie.value = layoutuse & 1;
		if (write(fduinput, &ie, sizeof(ie)) != sizeof(ie))
			fprintf(stderr, "error sending uinput event\n");
	} else if (row == 3 && pressed == 1) {
		// Backspace (100% pure backspace, never touches letters!)
		send_key(KEY_BACKSPACE);
	} else if (row == 4 && pressed == 0) {
		// Left Ctrl (Swapped to left side)
		ctrllock ^= 1;
		ie.type = EV_KEY;
		ie.code = KEY_LEFTCTRL;
		ie.value = ctrllock;
		if (write(fduinput, &ie, sizeof(ie)) != sizeof(ie))
			fprintf(stderr, "error sending uinput event\n");
	} else if (row == 4 && pressed == 1) {
		// Space
		send_key(KEY_SPACE);
	} else if (row == 4 && pressed == 2) {
		// Dot '.' (sebelah kiri Alt)
		send_key(KEY_DOT);
	} else if (row == 4 && pressed == 3) {
		// Right Alt (Swapped to right side)
		altlock ^= 1;
		ie.type = EV_KEY;
		ie.code = KEY_LEFTALT;
		ie.value = altlock;
		if (write(fduinput, &ie, sizeof(ie)) != sizeof(ie))
			fprintf(stderr, "error sending uinput event\n");
	} else if (row == 4 && pressed == 4) {
		// Enter
		send_key(KEY_ENTER);
	}
}

int reset_window_size(int fd)
{
	struct winsize win = { 0, 0, 0, 0 };

	if (ioctl(fd, TIOCGWINSZ, &win)) {
		if (errno != EINVAL) {
			perror("error resetting window size");
			return 0;
		}
		memset(&win, 0, sizeof(win));
	}

	win.ws_row += 2;
	if (!ioctl(fd, TIOCSWINSZ, (char *) &win)) {
		do {
			win.ws_row *= landscape ? 4 : 3;
			win.ws_row /= 2;
		} while (!ioctl(fd, TIOCSWINSZ, (char *) &win));
		do {
			win.ws_row--;
		} while (ioctl(fd, TIOCSWINSZ, (char *) &win));
	}

	return win.ws_row;
}

void sig_handler(int sig)
{
	done = 1;
}

int main(int argc, char *argv[])
{
	int opt;
	int fbfd = -1;
	int fdinput = -1;
	struct uinput_user_dev uidev;
	int tty;
	char str[11];
	int lasttty = -1;
	struct vt_stat vts;
	int currenttty = 0;
	FT_Library library;
	int orig_rows = 0;
	DIR *dir;
	struct dirent *ent;
	char *devname;
	int i;
	struct input_absinfo abs_x, abs_y;
	int x, y;
	struct input_event iev[64];
	int rd;
	int row = -1, pressed = -1;

	struct sigaction act;
	act.sa_handler = sig_handler;
	sigemptyset(&act.sa_mask);
	act.sa_flags = 0;
	sigaction(SIGTERM, &act, NULL);
	sigaction(SIGINT, &act, NULL);

	while ((opt = getopt(argc, argv, "d:f:r:h")) != -1) {
		switch (opt) {
			case 'd':
				device = optarg;
				break;
			case 'f':
				font = optarg;
				break;
			case 'r':
				rotate = strtol(optarg, NULL, 0);
				break;
			case 'h':
			default:
				puts("usage: fbkeyboard [options]");
				puts("possible options are:");
				puts(" -h: print this help");
				puts(" -d: set path to inputdevice");
				puts(" -f: set path to font");
				puts(" -r: set rotation");
				return 0;
		}
	}

	fbfd = open("/dev/fb0", O_RDWR);
	if (fbfd == -1) {
		perror("error: cannot open framebuffer device");
		exit(-1);
	}
	if (ioctl(fbfd, FBIOGET_FSCREENINFO, &finfo) == -1) {
		perror("error: reading fixed framebuffer information");
		exit(-1);
	}
	if (ioctl(fbfd, FBIOGET_VSCREENINFO, &vinfo) == -1) {
		perror("error: reading variable framebuffer information");
		exit(-1);
	}
	fbwidth = vinfo.xres;
	fbheight = vinfo.yres;
	fblinelength = finfo.line_length;
	switch (rotate) {
		case FB_ROTATE_UR:
		case FB_ROTATE_UD:
			landscape = fbheight < fbwidth;
			width = fbwidth;
			height = fbheight / (landscape ? 2 : 3) / 5;
			trowh = height * 0x10000 / fbheight;
			linelength = fblinelength;
			buflen = linelength * (height * 5 + 1);
			break;
		case FB_ROTATE_CW:
		case FB_ROTATE_CCW:
			landscape = fbheight > fbwidth;
			width = fbheight;
			height = fbwidth / (landscape ? 2 : 3) / 5;
			trowh = height * 0x10000 / fbwidth;
			linelength = height * 5 * 4;
			buflen = width * 4 * (height * 5 + 1);
			break;
	}

	if (FT_Init_FreeType(&library)) {
		perror("FT_Init_FreeType failed");
		exit(-1);
	}
	if (FT_New_Face(library, font, 0, &face)) {
		perror("unable to load font file");
		exit(-1);
	}
	if (FT_Set_Pixel_Sizes(face, height * 1 / 4, height * 1 / 4)) {
		perror("FT_Set_Pixel_Sizes failed");
		exit(-1);
	}

	if (device) {
		if ((fdinput = open(device, O_RDONLY)) == -1) {
			perror("error: cannot open input device");
			exit(-1);
		}
	} else {
		dir = opendir("/dev/input");
		if (dir == NULL) {
			perror("error: cannot open /dev/input");
			exit(-1);
		}
		while ((ent = readdir(dir)) != NULL) {
			if (strncmp(ent->d_name, "event", 5) == 0) {
				devname = malloc(12 + strlen(ent->d_name));
				sprintf(devname, "/dev/input/%s", ent->d_name);
				if ((fdinput = open(devname, O_RDONLY)) != -1) {
					if (ioctl(fdinput, EVIOCGABS(ABS_MT_POSITION_X), &abs_x) != -1) {
						free(devname);
						break;
					}
					close(fdinput);
				}
				free(devname);
			}
		}
		closedir(dir);
	}

	if ((ioctl(fdinput, EVIOCGABS(ABS_MT_POSITION_X), &abs_x) == -1) ||
	    (ioctl(fdinput, EVIOCGABS(ABS_MT_POSITION_Y), &abs_y) == -1)) {
		perror("error: getting touchscreen size");
		exit(-1);
	}
	twidth = abs_x.maximum;
	theight = abs_y.maximum;

	fduinput = open("/dev/uinput", O_WRONLY);
	if (fduinput == -1) {
		perror("error: cannot open uinput device /dev/uinput");
		exit(-1);
	}

	memset(&uidev, 0, sizeof(uidev));
	snprintf(uidev.name, UINPUT_MAX_NAME_SIZE, "fbkeyboard");
	uidev.id.bustype = BUS_USB;
	uidev.id.vendor = 0x1;
	uidev.id.product = 0x1;
	uidev.id.version = 1;

	ioctl(fduinput, UI_SET_EVBIT, EV_KEY);
	ioctl(fduinput, UI_SET_EVBIT, EV_SYN);

	for (i = 0; i < 256; i++)
		ioctl(fduinput, UI_SET_KEYBIT, i);

	if (write(fduinput, &uidev, sizeof(uidev)) < 0) {
		perror("error: write uinput device");
		exit(-1);
	}
	if (ioctl(fduinput, UI_DEV_CREATE) < 0) {
		perror("error: create uinput device");
		exit(-1);
	}

	memset(&ie, 0, sizeof(ie));

	buf = malloc(buflen);
	if (buf == 0) {
		perror("error: allocating memory");
		exit(-1);
	}

	fill_rect(0, 0, width - 1, height * 5, TERMCOLOR);
	draw_keyboard(row, pressed);
	show_fbkeyboard(fbfd);

	while (!done) {
		if ((tty = open("/dev/tty0", O_RDWR)) != -1) {
			if (ioctl(tty, VT_GETSTATE, &vts) != -1)
				currenttty = vts.v_active;
			close(tty);
			if (currenttty != lasttty) {
				sprintf(str, "/dev/tty%d", currenttty);
				if ((tty = open(str, O_RDWR)) != -1) {
					orig_rows = reset_window_size(tty);
					close(tty);
				}
				lasttty = currenttty;
				fill_rect(0, 0, width - 1, height * 5, TERMCOLOR);
				draw_keyboard(row, pressed);
				show_fbkeyboard(fbfd);
			}
		}

		rd = read(fdinput, iev, sizeof(struct input_event) * 64);
		for (i = 0; i < rd / sizeof(struct input_event); i++) {
			if (iev[i].type == EV_ABS) {
				if (iev[i].code == ABS_MT_POSITION_X)
					x = iev[i].value * 0x10000 / twidth;
				else if (iev[i].code == ABS_MT_POSITION_Y)
					y = iev[i].value * 0x10000 / theight;
			} else if (iev[i].type == EV_KEY && iev[i].code == BTN_TOUCH) {
				if (iev[i].value == 1) {
					identify_touched_key(x, y, &row, &pressed);
					fill_rect(0, 0, width - 1, height * 5, TERMCOLOR);
					draw_keyboard(row, pressed);
					show_fbkeyboard(fbfd);
					send_uinput_event(row, pressed);
				} else if (iev[i].value == 0) {
					row = -1;
					pressed = -1;
					fill_rect(0, 0, width - 1, height * 5, TERMCOLOR);
					draw_keyboard(row, pressed);
					show_fbkeyboard(fbfd);
				}
			}
		}
	}

	if (orig_rows) {
		sprintf(str, "/dev/tty%d", currenttty);
		if ((tty = open(str, O_RDWR)) != -1) {
			struct winsize win = { orig_rows, 0, 0, 0 };
			ioctl(tty, TIOCSWINSZ, (char *) &win);
			close(tty);
		}
	}

	ioctl(fduinput, UI_DEV_DESTROY);
	close(fduinput);
	close(fdinput);
	close(fbfd);
	free(buf);
	FT_Done_Face(face);
	FT_Done_FreeType(library);

	return 0;
}
