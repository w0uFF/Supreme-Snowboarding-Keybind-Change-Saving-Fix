/* Freestanding 32-bit test of the actual assembled routines with mock Win32 APIs. */
typedef unsigned int u32;
#define STDCALL __attribute__((stdcall))
extern u32 active,ready,baseline[8],imp_create,imp_read,imp_write,imp_close,imp_move,imp_delete;
extern void load_bindings(void),save_bindings(void);
static u32 defaults[8]={0x24,0x27,0x2a,0x3a,0x3b,0x38,0x39,0x27};
static u32 menu[0x240/4], objects[8][6], vec[8], keys[8];
static u32 disk[10],temp[10], disklen, writes, moves, deletes, failwrite, failmove;
static void copy(u32 *d,const u32*s,u32 n){while(n--)*d++=*s++;}
static int eq(const u32*a,const u32*b,u32 n){while(n--)if(*a++!=*b++)return 0;return 1;}
static u32 STDCALL create(char *path,u32 access,u32 share,u32 security,u32 disposition,u32 attr,u32 template){(void)path;(void)access;(void)share;(void)security;(void)attr;(void)template;return disposition==3?(disklen?10:~0u):20;}
static u32 STDCALL readfile(u32 h,u32 *buf,u32 n,u32 *count,u32 overlap){(void)h;(void)n;(void)overlap;copy(buf,disk,(disklen+3)/4);*count=disklen;return 1;}
static u32 STDCALL writefile(u32 h,u32 *buf,u32 n,u32 *count,u32 overlap){(void)h;(void)overlap;writes++;copy(temp,buf,n/4);*count=failwrite?12:n;return 1;}
static u32 STDCALL closefile(u32 h){(void)h;return 1;}
static u32 STDCALL movefile(char *src,char *dst,u32 flags){(void)src;(void)dst;(void)flags;moves++;if(failmove)return 0;copy(disk,temp,9);disklen=36;return 1;}
static u32 STDCALL deletefile(char *p){(void)p;deletes++;return 1;}
static void load(void){__asm__ volatile("call load_bindings"::"S"(keys):"eax","ecx","edx","memory","cc");}
static void save(void){__asm__ volatile("call save_bindings"::"a"(menu):"ecx","edx","memory","cc");}
static void set_ui(void){u32 i;for(i=0;i<8;i++){vec[i]=(u32)objects[i];objects[i][5]=keys[i<2?(i^1):i];}menu[0x22c/4]=(u32)vec;menu[0x230/4]=(u32)(vec+8);}
static void die(u32 code){__asm__ volatile("int $0x80"::"a"(1),"b"(code));__builtin_unreachable();}
#define CHECK(x,n) do {if(!(x))die(n);}while(0)
void _start(void){
 imp_create=(u32)create;imp_read=(u32)readfile;imp_write=(u32)writefile;imp_close=(u32)closefile;imp_move=(u32)movefile;imp_delete=(u32)deletefile;
 active=(u32)menu;copy(keys,defaults,8);load();CHECK(ready==1&&eq(keys,defaults,8)&&eq(baseline,defaults,8),1);
 set_ui();save();CHECK(writes==0,2);
 objects[0][5]=12;objects[1][5]=13;objects[7][5]=99;save();CHECK(writes==1&&moves==1&&disklen==36&&disk[0]==0x31424b53&&disk[1]==13&&disk[2]==12&&disk[8]==99,3);
 save();CHECK(writes==1,4);
 copy(keys,defaults,8);load();CHECK(keys[0]==13&&keys[1]==12&&keys[7]==99,5);set_ui();save();CHECK(writes==1,6);
 disk[4]=256;copy(keys,defaults,8);load();CHECK(eq(keys,defaults,8),7);
 disk[4]=0;disklen=35;copy(keys,defaults,8);load();CHECK(eq(keys,defaults,8),8);
 disklen=37;copy(keys,defaults,8);load();CHECK(eq(keys,defaults,8),9);
 disklen=36;disk[0]=0;copy(keys,defaults,8);load();CHECK(eq(keys,defaults,8),10);
 set_ui();objects[2][5]=88;failwrite=1;save();CHECK(writes==2&&moves==1&&deletes==1&&baseline[2]==defaults[2],11);
 failwrite=0;failmove=1;save();CHECK(writes==3&&moves==2&&deletes==2&&baseline[2]==defaults[2],12);
 failmove=0;save();CHECK(writes==4&&moves==3&&disk[3]==88&&baseline[2]==88,13);
 objects[2][5]=100;menu[0x230/4]-=4;save();CHECK(writes==4,14);
 menu[0x230/4]+=4;objects[3][5]=999;save();CHECK(writes==4,15);
 objects[3][5]=keys[3];active=0;save();CHECK(writes==4,16);
 die(0);
}
