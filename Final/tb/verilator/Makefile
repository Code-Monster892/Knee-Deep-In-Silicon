.PHONY: all clean software

all: software
	@echo "--- Compiling with Verilator (Optimized for Speed) ---"
	verilator -Wall -Wno-DECLFILENAME -Wno-UNOPTFLAT -Wno-EOFNEWLINE -Wno-WIDTHTRUNC -Wno-UNUSEDSIGNAL -Wno-CASEINCOMPLETE -Wno-SYNCASYNCNET -Wno-PINMISSING -LDFLAGS "-lSDL2" -CFLAGS "-O3 -march=native" --cc ../../src/*.sv --exe main.cpp --top-module cpu --build -j 0
	@echo "--- Running Simulation ---"
	./obj_dir/Vcpu

doom1_wad.c: doom1.wad
	@echo "--- Converting WAD to C Array ---"
	python3 -c "import sys; data=open('doom1.wad','rb').read(); out=open('doom1_wad.c','w'); out.write('unsigned char doom1_wad[] = {'); out.write(','.join(map(str,data))); out.write('};\nunsigned int doom1_wad_len = %d;\n' % len(data)); out.close()"

DOOM_CORE_SRCS = dummy.c am_map.c doomdef.c doomstat.c dstrings.c d_event.c d_items.c d_iwad.c d_loop.c d_main.c d_mode.c d_net.c f_finale.c f_wipe.c g_game.c hu_lib.c hu_stuff.c info.c i_cdmus.c i_endoom.c i_joystick.c i_scale.c i_sound.c i_system.c i_timer.c memio.c m_argv.c m_bbox.c m_cheat.c m_config.c m_controls.c m_fixed.c m_menu.c m_misc.c m_random.c p_ceilng.c p_doors.c p_enemy.c p_floor.c p_inter.c p_lights.c p_map.c p_maputl.c p_mobj.c p_plats.c p_pspr.c p_saveg.c p_setup.c p_sight.c p_spec.c p_switch.c p_telept.c p_tick.c p_user.c r_bsp.c r_data.c r_draw.c r_main.c r_plane.c r_segs.c r_sky.c r_things.c sha1.c sounds.c statdump.c st_lib.c st_stuff.c s_sound.c tables.c v_video.c wi_stuff.c w_checksum.c w_file.c w_main.c w_wad.c z_zone.c w_file_stdc.c i_input.c i_video.c doomgeneric.c
DOOM_SRCS = $(addprefix doomgeneric/doomgeneric/, $(DOOM_CORE_SRCS))

doom1_wad.o: doom1_wad.c
	@echo "--- Compiling doom1_wad.c ---"
	riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 -O0 -c doom1_wad.c -o doom1_wad.o

software: doom1_wad.o
	@echo "--- Compiling DOOM Bare-Metal ---"
	riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 -O3 -T link.ld -nostartfiles --specs=picolibc.specs \
	-I./doomgeneric/doomgeneric \
	-DDOOMGENERIC_RESX=320 -DDOOMGENERIC_RESY=200 \
	crt0.s syscalls.c doomgeneric_riscv.c doom1_wad.o \
	$(DOOM_SRCS) \
	-o doom.elf
	
	@echo "--- Extracting Binary ---"
	riscv64-unknown-elf-objcopy -O binary doom.elf doom.bin
	python3 -c "import sys; b=sys.stdin.buffer.read(); b += b'\x00' * ((4 - len(b) % 4) % 4); print('\n'.join(b[i:i+4][::-1].hex() for i in range(0,len(b),4)))" < doom.bin > firmware.hex

clean:
	rm -rf obj_dir waveform.vcd doom.elf doom.bin firmware.hex doom1_wad.c doom1_wad.o doom_qemu.elf

software-qemu: doom1_wad.o
	@echo "--- Compiling DOOM Bare-Metal for QEMU ---"
	riscv64-unknown-elf-gcc -march=rv32im -mabi=ilp32 -O3 -T link_qemu.ld -nostartfiles --specs=picolibc.specs \
	-I./doomgeneric/doomgeneric \
	-DDOOMGENERIC_RESX=320 -DDOOMGENERIC_RESY=200 \
	crt0.s syscalls.c doomgeneric_riscv.c doom1_wad.o \
	$(DOOM_SRCS) \
	-o doom_qemu.elf

qemu: software-qemu
	@echo "--- Running QEMU ---"
	qemu-system-riscv32 -M virt -m 32M -nographic -kernel doom_qemu.elf -bios none
