.intel_syntax noprefix
.code32
.section .text
.global startup_hook, input_hook, teardown_hook, load_bindings, save_bindings
.equ ORIGINAL_MENU_ACTION, 0x46d4b8
.equ ROOT_OBJECT, 0x4889c4
.equ MAGIC, 0x31424b53
# Original startup allocates and fills the eight gameplay key codes in EAX.
startup_hook:
    push 1
    mov [ebp+0x238], eax
    pushfd
    pushad
    mov dword ptr [active], ebp
    mov dword ptr [ready], 0
    test eax,eax
    jz startup_done
    mov esi,eax
    call load_bindings
startup_done:
    popad
    popfd
    jmp 0x4485a0

# Preserve the original fastcall and its stack arguments exactly.
input_hook:
    call dword ptr [ORIGINAL_MENU_ACTION]
    pushfd
    pushad
    mov eax,[ROOT_OBJECT]
    test eax,eax
    jz input_done
    mov eax,[eax+0x14]
    call save_bindings
input_done:
    popad
    popfd
    jmp 0x45388d

# Save once more on normal menu-state destruction, before freeing key data.
teardown_hook:
    pushfd
    pushad
    mov eax,esi
    call save_bindings
    cmp esi,[active]
    jne teardown_done
    mov dword ptr [active],0
    mov dword ptr [ready],0
teardown_done:
    popad
    popfd
    mov eax,[esi+0x238]
    jmp 0x44cd91

# ESI = allocated default array, preserved by Win32 stdcall.
load_bindings:
    push ebx
    push edi
    push ebp
    sub esp,44
    mov ebp,esp
    push 0
    push 0x80
    push 3
    push 0
    push 1
    push 0x80000000
    push offset save_path
    call dword ptr [imp_create]
    cmp eax,-1
    je load_baseline
    mov ebx,eax
    push 0
    lea eax,[ebp+40]
    push eax
    push 37
    push ebp
    push ebx
    call dword ptr [imp_read]
    mov edi,eax
    push ebx
    call dword ptr [imp_close]
    test edi,edi
    jz load_baseline
    cmp dword ptr [ebp+40],36
    jne load_baseline
    cmp dword ptr [ebp],MAGIC
    jne load_baseline
    xor ecx,ecx
load_check:
    cmp dword ptr [ebp+ecx*4+4],255
    ja load_baseline
    inc ecx
    cmp ecx,8
    jb load_check
    xor ecx,ecx
load_copy:
    mov eax,[ebp+ecx*4+4]
    mov [esi+ecx*4],eax
    inc ecx
    cmp ecx,8
    jb load_copy
load_baseline:
    xor ecx,ecx
baseline_copy:
    mov eax,[esi+ecx*4]
    mov [baseline+ecx*4],eax
    inc ecx
    cmp ecx,8
    jb baseline_copy
    mov dword ptr [ready],1
    add esp,44
    pop ebp
    pop edi
    pop ebx
    ret

# EAX = menu state. UI order differs from gameplay array in first two slots.
save_bindings:
    cmp dword ptr [ready],1
    jne save_return
    test eax,eax
    jz save_return
    cmp eax,[active]
    jne save_return
    push ebx
    push esi
    push edi
    push ebp
    sub esp,44
    mov ebp,esp
    mov esi,[eax+0x22c]
    test esi,esi
    jz save_exit
    mov edx,[eax+0x230]
    sub edx,esi
    cmp edx,32
    jne save_exit
    mov dword ptr [ebp],MAGIC
    xor ecx,ecx
save_collect:
    mov edx,[esi+ecx*4]
    test edx,edx
    jz save_exit
    mov edx,[edx+0x14]
    cmp edx,255
    ja save_exit
    mov eax,ecx
    cmp eax,2
    jae save_store
    xor eax,1
save_store:
    mov [ebp+eax*4+4],edx
    inc ecx
    cmp ecx,8
    jb save_collect
    xor ecx,ecx
save_compare:
    mov eax,[ebp+ecx*4+4]
    cmp eax,[baseline+ecx*4]
    jne save_write
    inc ecx
    cmp ecx,8
    jb save_compare
    jmp save_exit
save_write:
    push 0
    push 0x80
    push 2
    push 0
    push 0
    push 0x40000000
    push offset temp_path
    call dword ptr [imp_create]
    cmp eax,-1
    je save_exit
    mov ebx,eax
    push 0
    lea eax,[ebp+40]
    push eax
    push 36
    push ebp
    push ebx
    call dword ptr [imp_write]
    mov edi,eax
    push ebx
    call dword ptr [imp_close]
    test eax,eax
    jz save_cleanup
    test edi,edi
    jz save_cleanup
    cmp dword ptr [ebp+40],36
    jne save_cleanup
    push 9
    push offset save_path
    push offset temp_path
    call dword ptr [imp_move]
    test eax,eax
    jz save_cleanup
    xor ecx,ecx
save_baseline:
    mov eax,[ebp+ecx*4+4]
    mov [baseline+ecx*4],eax
    inc ecx
    cmp ecx,8
    jb save_baseline
    jmp save_exit
save_cleanup:
    push offset temp_path
    call dword ptr [imp_delete]
save_exit:
    add esp,44
    pop ebp
    pop edi
    pop esi
    pop ebx
save_return:
    ret

.section .data
.global active,ready,baseline,imp_create,imp_read,imp_write,imp_close,imp_move,imp_delete,save_path,temp_path
active: .long 0
ready: .long 0
baseline: .zero 32
save_path: .asciz "Saved_Data/Keyboard_Bindings.bin"
temp_path: .asciz "Saved_Data/Keyboard_Bindings.tmp"
.balign 4
imp_create: .long 0
imp_read: .long 0
imp_write: .long 0
imp_close: .long 0
imp_move: .long 0
imp_delete: .long 0
.long 0
