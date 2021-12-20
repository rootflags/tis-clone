#!/bin/sh

. /etc/tis-clone.cfg

cd ${FSM_URLBASE}
mkisofs -o ${DOWNLOAD_TO}/TheCompleteTLCFSM.iso \
	-b isolinux/isolinux.bin \
	-c isolinux/boot.cat \
	-no-emul-boot -boot-load-size 4 -boot-info-table -J -R \
	-m TheCompleteTLCFSM*.iso \
	-V "Complete Land Cruiser FSM 2021" .
