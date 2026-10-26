GoldenrodCity_DepartmentStore_5F_hns_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, GoldenrodDeptElevator_OnFrame
	.byte 0


GoldenrodDeptStore5_EventScript_Lass::
	lock
	faceplayer
	msgbox GoldenrodDeptStore_Text_5FLass, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore5_EventScript_PokefanM::
	lock
	faceplayer
	msgbox GoldenrodDeptStore_Text_5FPokefanM, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore5_EventScript_Girl::
	lock
	faceplayer
	msgbox GoldenrodDeptStore_Text_Girl, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore5_EventScript_Sign::
	lock
	faceplayer
	msgbox GoldenrodDeptStore_Text_5FDirectory, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore5_EventScript_Receptionist::
	lock
	faceplayer
	goto_if_set FLAG_GOT_RETURN, GoldenrodDeptStore5_EventScript_Receptionist_Already
	msgbox GoldenrodDeptStore_Text_5FReceptionistOhYourMon, MSGBOX_DEFAULT
	closemessage
	specialvar VAR_RESULT, GetLeadMonFriendshipScore
	goto_if_ge VAR_RESULT, FRIENDSHIP_150_TO_199, GoldenrodDeptStore5_EventScript_Receptionist_GiveReturn
	msgbox GoldenrodDeptStore_Text_5FReceptionistPutInSomeMoreEffort, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore5_EventScript_Receptionist_GiveReturn::
	giveitem ITEM_TM_RETURN
	setflag FLAG_GOT_RETURN
	msgbox GoldenrodDeptStore_Text_5FReceptionistThisMoveShouldBePerfect, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore5_EventScript_Receptionist_Already::
	msgbox GoldenrodDeptStore_Text_5FReceptionistWait, MSGBOX_DEFAULT
	closemessage
	release
	end

GoldenrodDeptStore_Text_5FReceptionistOhYourMon:
    .string "Hello. Oh, your POKéMON…$"

GoldenrodDeptStore_Text_5FReceptionistWait:
    .string "Wait, I already gave you that TM!$"

GoldenrodDeptStore_Text_5FReceptionistPutInSomeMoreEffort:
	.string "Hmm…\n"
	.string "It's not bad, but it's also not good.\p"
	.string "You, as the TRAINER, need to put in\n"
	.string "some more effort.$"

GoldenrodDeptStore_Text_5FReceptionistThisMoveShouldBePerfect:
    .string "It's very attached to you.\p"
    .string "This move should be perfect for a\n"
    .string "pair like you.$"

GoldenrodDeptStore_Text_5FLass:
    .string "During the day, a lady comes to check\n"
    .string "out POKéMON.\p"
    .string "She even gives away TMs!$"

GoldenrodDeptStore_Text_5FPokefanM:
    .string "You can't rename a POKéMON you get\n"
    .string "in a trade.\p"
    .string "The name is a reflection of the\n"
    .string "original trainer's feelings for it.$"

GoldenrodDeptStore_Text_Girl:
	.string "The lady gave me RETURN!\n"
    .string "My POKéMON must really like me!$"

@ Crystal Imperium: the TM shop every Poke Mart's TM clerk has, more TMs with each badge
@ (EventScript_TMShop, data/scripts/tm_shop_hns.inc from tools/crystal_imperium/tm_list.py).
GoldenrodDeptStore5_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	call EventScript_TMShop
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end


GoldenrodDeptStore_Text_5FDirectory:
    .string "Customize Your POKéMON\p"
    .string "5F TM CORNER$"

@ Crystal Imperium: Mega Ring gift after the third badge, then a Mega Stone shop
@ whose stock grows with progress (3 / 6 / 8 badges, counted, then the Johto title).
GoldenrodDeptStore5_EventScript_MegaSpecialist::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, GoldenrodDeptStore5_EventScript_MegaNotReady
	goto_if_set FLAG_RECEIVED_MEGA_RING, GoldenrodDeptStore5_EventScript_MegaShop
	msgbox GoldenrodDeptStore5_Text_MegaIntro, MSGBOX_DEFAULT
	giveitem ITEM_MEGA_RING
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_MEGA_RING
	msgbox GoldenrodDeptStore5_Text_MegaExplain, MSGBOX_DEFAULT
GoldenrodDeptStore5_EventScript_MegaShop::
	message gText_HowMayIServeYou
	waitmessage
	goto_if_set FLAG_IS_CHAMPION, GoldenrodDeptStore5_EventScript_MegaShop4
	specialvar VAR_RESULT, GetBadgeCount
	goto_if_ge VAR_RESULT, 8, GoldenrodDeptStore5_EventScript_MegaShop3
	goto_if_ge VAR_RESULT, 6, GoldenrodDeptStore5_EventScript_MegaShop2
	pokemart GoldenrodDeptStore5_MegaStones1
	goto GoldenrodDeptStore5_EventScript_MegaShopDone
GoldenrodDeptStore5_EventScript_MegaShop2::
	pokemart GoldenrodDeptStore5_MegaStones2
	goto GoldenrodDeptStore5_EventScript_MegaShopDone
GoldenrodDeptStore5_EventScript_MegaShop3::
	pokemart GoldenrodDeptStore5_MegaStones3
	goto GoldenrodDeptStore5_EventScript_MegaShopDone
GoldenrodDeptStore5_EventScript_MegaShop4::
	pokemart GoldenrodDeptStore5_MegaStones4
	goto GoldenrodDeptStore5_EventScript_MegaShopDone
GoldenrodDeptStore5_EventScript_MegaShopDone::
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

GoldenrodDeptStore5_EventScript_MegaNotReady::
	msgbox GoldenrodDeptStore5_Text_MegaNotReady, MSGBOX_DEFAULT
	release
	end

GoldenrodDeptStore5_Text_MegaNotReady:
	.string "I study MEGA EVOLUTION.\p"
	.string "Come back when you have\n"
	.string "three JOHTO BADGES.$"

GoldenrodDeptStore5_Text_MegaIntro:
	.string "Three BADGES already?\n"
	.string "Then you're ready for this.\p"
	.string "Take my spare MEGA RING!$"

GoldenrodDeptStore5_Text_MegaExplain:
	.string "A POKéMON holding its MEGA\n"
	.string "STONE can MEGA EVOLVE once\l"
	.string "per battle.\p"
	.string "I sell MEGA STONES, and I'll\n"
	.string "stock rarer ones as you earn\l"
	.string "more BADGES.$"

	.align 2
GoldenrodDeptStore5_MegaStones1:
	.2byte ITEM_BEEDRILLITE
	.2byte ITEM_PIDGEOTITE
	.2byte ITEM_AMPHAROSITE
	.2byte ITEM_HERACRONITE
	.2byte ITEM_PINSIRITE
	.2byte ITEM_AUDINITE
	.2byte ITEM_LOPUNNITE
	.2byte ITEM_MANECTITE
	.2byte ITEM_SABLENITE
	.2byte ITEM_BANETTITE
	pokemartlistend

	.align 2
GoldenrodDeptStore5_MegaStones2:
	.2byte ITEM_BEEDRILLITE
	.2byte ITEM_PIDGEOTITE
	.2byte ITEM_AMPHAROSITE
	.2byte ITEM_HERACRONITE
	.2byte ITEM_PINSIRITE
	.2byte ITEM_AUDINITE
	.2byte ITEM_LOPUNNITE
	.2byte ITEM_MANECTITE
	.2byte ITEM_SABLENITE
	.2byte ITEM_BANETTITE
	.2byte ITEM_VENUSAURITE
	.2byte ITEM_CHARIZARDITE_X
	.2byte ITEM_CHARIZARDITE_Y
	.2byte ITEM_BLASTOISINITE
	.2byte ITEM_SCEPTILITE
	.2byte ITEM_BLAZIKENITE
	.2byte ITEM_SWAMPERTITE
	.2byte ITEM_GENGARITE
	.2byte ITEM_ALAKAZITE
	.2byte ITEM_SLOWBRONITE
	.2byte ITEM_STEELIXITE
	.2byte ITEM_SCIZORITE
	.2byte ITEM_HOUNDOOMINITE
	.2byte ITEM_ABSOLITE
	.2byte ITEM_GLALITITE
	.2byte ITEM_ABOMASITE
	.2byte ITEM_ALTARIANITE
	.2byte ITEM_CAMERUPTITE
	.2byte ITEM_SHARPEDONITE
	.2byte ITEM_AGGRONITE
	.2byte ITEM_MEDICHAMITE
	.2byte ITEM_GARDEVOIRITE
	.2byte ITEM_GALLADITE
	.2byte ITEM_AERODACTYLITE
	.2byte ITEM_KANGASKHANITE
	.2byte ITEM_MAWILITE
	pokemartlistend

	.align 2
GoldenrodDeptStore5_MegaStones3:
	.2byte ITEM_BEEDRILLITE
	.2byte ITEM_PIDGEOTITE
	.2byte ITEM_AMPHAROSITE
	.2byte ITEM_HERACRONITE
	.2byte ITEM_PINSIRITE
	.2byte ITEM_AUDINITE
	.2byte ITEM_LOPUNNITE
	.2byte ITEM_MANECTITE
	.2byte ITEM_SABLENITE
	.2byte ITEM_BANETTITE
	.2byte ITEM_VENUSAURITE
	.2byte ITEM_CHARIZARDITE_X
	.2byte ITEM_CHARIZARDITE_Y
	.2byte ITEM_BLASTOISINITE
	.2byte ITEM_SCEPTILITE
	.2byte ITEM_BLAZIKENITE
	.2byte ITEM_SWAMPERTITE
	.2byte ITEM_GENGARITE
	.2byte ITEM_ALAKAZITE
	.2byte ITEM_SLOWBRONITE
	.2byte ITEM_STEELIXITE
	.2byte ITEM_SCIZORITE
	.2byte ITEM_HOUNDOOMINITE
	.2byte ITEM_ABSOLITE
	.2byte ITEM_GLALITITE
	.2byte ITEM_ABOMASITE
	.2byte ITEM_ALTARIANITE
	.2byte ITEM_CAMERUPTITE
	.2byte ITEM_SHARPEDONITE
	.2byte ITEM_AGGRONITE
	.2byte ITEM_MEDICHAMITE
	.2byte ITEM_GARDEVOIRITE
	.2byte ITEM_GALLADITE
	.2byte ITEM_AERODACTYLITE
	.2byte ITEM_KANGASKHANITE
	.2byte ITEM_MAWILITE
	.2byte ITEM_GYARADOSITE
	.2byte ITEM_LUCARIONITE
	.2byte ITEM_TYRANITARITE
	.2byte ITEM_SALAMENCITE
	.2byte ITEM_METAGROSSITE
	.2byte ITEM_GARCHOMPITE
	pokemartlistend

	.align 2
@ Every Mega Stone this game uses: the MEGA code (src/cheat_codes.c) gives these too
GoldenrodDeptStore5_MegaStones4::
	.2byte ITEM_BEEDRILLITE
	.2byte ITEM_PIDGEOTITE
	.2byte ITEM_AMPHAROSITE
	.2byte ITEM_HERACRONITE
	.2byte ITEM_PINSIRITE
	.2byte ITEM_AUDINITE
	.2byte ITEM_LOPUNNITE
	.2byte ITEM_MANECTITE
	.2byte ITEM_SABLENITE
	.2byte ITEM_BANETTITE
	.2byte ITEM_VENUSAURITE
	.2byte ITEM_CHARIZARDITE_X
	.2byte ITEM_CHARIZARDITE_Y
	.2byte ITEM_BLASTOISINITE
	.2byte ITEM_SCEPTILITE
	.2byte ITEM_BLAZIKENITE
	.2byte ITEM_SWAMPERTITE
	.2byte ITEM_GENGARITE
	.2byte ITEM_ALAKAZITE
	.2byte ITEM_SLOWBRONITE
	.2byte ITEM_STEELIXITE
	.2byte ITEM_SCIZORITE
	.2byte ITEM_HOUNDOOMINITE
	.2byte ITEM_ABSOLITE
	.2byte ITEM_GLALITITE
	.2byte ITEM_ABOMASITE
	.2byte ITEM_ALTARIANITE
	.2byte ITEM_CAMERUPTITE
	.2byte ITEM_SHARPEDONITE
	.2byte ITEM_AGGRONITE
	.2byte ITEM_MEDICHAMITE
	.2byte ITEM_GARDEVOIRITE
	.2byte ITEM_GALLADITE
	.2byte ITEM_AERODACTYLITE
	.2byte ITEM_KANGASKHANITE
	.2byte ITEM_MAWILITE
	.2byte ITEM_GYARADOSITE
	.2byte ITEM_LUCARIONITE
	.2byte ITEM_TYRANITARITE
	.2byte ITEM_SALAMENCITE
	.2byte ITEM_METAGROSSITE
	.2byte ITEM_GARCHOMPITE
	.2byte ITEM_MEWTWONITE_X
	.2byte ITEM_MEWTWONITE_Y
	.2byte ITEM_LATIASITE
	.2byte ITEM_LATIOSITE
	.2byte ITEM_DIANCITE
	pokemartlistend
