@ Crystal Imperium: Emerald Imperium's cheat codes (DECISIONS.md D37), typed at the NES in the
@ player's room: src/cheat_codes.c has the codes and their aliases (DEXALL or DXA, CAUGHTALL or
@ CAL, EZCATCH or EZC, MEGA, SHINYS or SHS, MAXMONEY or MMY, MONO, SHINYR or SHR).
EventScript_CheatCodeConsole::
	msgbox CheatCode_Text_EnterACode, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CheatCode_TimeToGo
	fadescreen FADE_TO_BLACK
	special EnterCode
	waitstate
	callnative CheatCode_Find
	switch VAR_RESULT
	case CHEAT_CODE_DEXALL, CheatCode_DexAll
	case CHEAT_CODE_CAUGHTALL, CheatCode_CaughtAll
	case CHEAT_CODE_EZCATCH, CheatCode_EZCatch
	case CHEAT_CODE_MEGA, CheatCode_Mega
	case CHEAT_CODE_SHINYS, CheatCode_ShinyStarters
	case CHEAT_CODE_MAXMONEY, CheatCode_MaxMoney
	case CHEAT_CODE_MONO, CheatCode_Mono
	case CHEAT_CODE_SHINYR, CheatCode_ShinyRoamers
	msgbox CheatCode_Text_NothingHappened, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_TimeToGo:
	msgbox CheatCode_Text_TimeToGo, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_DexAll:
	msgbox CheatCode_Text_DexAll, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_CaughtAll:
	callnative CheatCode_MarkAllCaught
	playse SE_SUCCESS
	msgbox CheatCode_Text_CaughtAll, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_EZCatch:
	callnative CheatCode_ToggleEasyCatch
	playse SE_SUCCESS
	goto_if_eq VAR_RESULT, FALSE, CheatCode_EZCatchOff
	msgbox CheatCode_Text_EZCatchOn, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_EZCatchOff:
	msgbox CheatCode_Text_EZCatchOff, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_Mega:
	callnative CheatCode_GiveMegaStones
	call_if_eq VAR_0x8006, TRUE, CheatCode_MegaRing
	goto_if_eq VAR_0x8005, 0, CheatCode_MegaNoneGiven
	playfanfare MUS_OBTAIN_ITEM
	buffernumberstring STR_VAR_1, VAR_0x8005
	msgbox CheatCode_Text_MegaStones, MSGBOX_DEFAULT
	waitfanfare
	goto_if_eq VAR_RESULT, 0, CheatCode_End
CheatCode_MegaNoRoom:
	buffernumberstring STR_VAR_1, VAR_RESULT
	msgbox CheatCode_Text_MegaNoRoom, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_MegaRing:
	playfanfare MUS_OBTAIN_ITEM
	msgbox CheatCode_Text_MegaRing, MSGBOX_DEFAULT
	waitfanfare
	return

CheatCode_MegaNoneGiven:
	goto_if_ne VAR_RESULT, 0, CheatCode_MegaNoRoom
	msgbox CheatCode_Text_MegaAlready, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_ShinyStarters:
	goto_if_set FLAG_SYS_POKEMON_GET, CheatCode_TooLate
	playse SE_SUCCESS
	goto_if_set FLAG_CODE_SHINY_STARTERS, CheatCode_ShinyStartersOff
	setflag FLAG_CODE_SHINY_STARTERS
	msgbox CheatCode_Text_ShinyStartersOn, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_ShinyStartersOff:
	clearflag FLAG_CODE_SHINY_STARTERS
	msgbox CheatCode_Text_ShinyStartersOff, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_MaxMoney:
	callnative CheatCode_SetMaxMoney
	playse SE_SHOP
	msgbox CheatCode_Text_MaxMoney, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_Mono:
	goto_if_set FLAG_SYS_POKEMON_GET, CheatCode_TooLate
	message CheatCode_Text_MonoChooseType
	waitmessage
	dynmultichoice 19, 0, FALSE, 6, 0, DYN_MULTICHOICE_CB_NONE, CheatCode_Text_Off, CheatCode_Text_Fighting, CheatCode_Text_Flying, CheatCode_Text_Poison, CheatCode_Text_Ground, CheatCode_Text_Rock, CheatCode_Text_Bug, CheatCode_Text_Ghost, CheatCode_Text_Steel, CheatCode_Text_Electric, CheatCode_Text_Psychic, CheatCode_Text_Ice, CheatCode_Text_Dragon, CheatCode_Text_Dark, CheatCode_Text_Normal, CheatCode_Text_Fairy
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, CheatCode_End
	callnative CheatCode_SetMonoType
	playse SE_SUCCESS
	goto_if_eq VAR_MONO_STARTER_TYPE, 0, CheatCode_MonoOff
	msgbox CheatCode_Text_MonoOn, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_MonoOff:
	msgbox CheatCode_Text_MonoOff, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_ShinyRoamers:
	callnative CheatCode_MakeRoamersShiny
	playse SE_SUCCESS
	msgbox CheatCode_Text_ShinyRoamers, MSGBOX_DEFAULT
	goto CheatCode_End

CheatCode_TooLate:
	msgbox CheatCode_Text_TooLate, MSGBOX_DEFAULT
CheatCode_End:
	releaseall
	end

CheatCode_Text_EnterACode:
	.string "{PLAYER} turned on the NES.\n"
	.string "Enter a code?$"

CheatCode_Text_TimeToGo:
	.string "…Okay!\n"
	.string "It's time to go!$"

CheatCode_Text_NothingHappened:
	.string "Nothing happened…$"

CheatCode_Text_DexAll:
	.string "The DEXNAV already shows every\n"
	.string "POKéMON, caught or not!$"

CheatCode_Text_CaughtAll:
	.string "Every POKéMON is now caught\n"
	.string "in the NATIONAL POKéDEX!$"

CheatCode_Text_EZCatchOn:
	.string "EASY CATCH is on: every\n"
	.string "POKé BALL catches!$"

CheatCode_Text_EZCatchOff:
	.string "EASY CATCH is off.$"

CheatCode_Text_MegaRing:
	.string "{PLAYER} got the MEGA RING!$"

CheatCode_Text_MegaStones:
	.string "{PLAYER} got {STR_VAR_1} MEGA STONES:\n"
	.string "one for every MEGA EVOLUTION!$"

CheatCode_Text_MegaNoRoom:
	.string "{STR_VAR_1} MEGA STONES didn't fit.\p"
	.string "Make room in your BAG or PC, then\n"
	.string "enter MEGA again for the rest.$"

CheatCode_Text_MegaAlready:
	.string "You already have every\n"
	.string "MEGA STONE!$"

CheatCode_Text_ShinyStartersOn:
	.string "SHINY STARTERS on: PROF. ELM's\n"
	.string "POKéMON will all be shiny!$"

CheatCode_Text_ShinyStartersOff:
	.string "SHINY STARTERS off.$"

CheatCode_Text_MaxMoney:
	.string "{PLAYER}'s money went up\n"
	.string "to the maximum!$"

CheatCode_Text_MonoChooseType:
	.string "MONOTYPE STARTERS: choose\n"
	.string "PROF. ELM's POKéMON's type.$"

CheatCode_Text_MonoOn:
	.string "PROF. ELM's three POKéMON will\n"
	.string "all be of that type!$"

CheatCode_Text_MonoOff:
	.string "MONOTYPE STARTERS off: PROF. ELM\n"
	.string "has his usual POKéMON.$"

CheatCode_Text_ShinyRoamers:
	.string "Every roaming POKéMON\n"
	.string "is now shiny!$"

CheatCode_Text_TooLate:
	.string "That code only works before you\n"
	.string "choose your first POKéMON.$"

CheatCode_Text_Off:
	.string "OFF$"

CheatCode_Text_Fighting:
	.string "FIGHTING$"

CheatCode_Text_Flying:
	.string "FLYING$"

CheatCode_Text_Poison:
	.string "POISON$"

CheatCode_Text_Ground:
	.string "GROUND$"

CheatCode_Text_Rock:
	.string "ROCK$"

CheatCode_Text_Bug:
	.string "BUG$"

CheatCode_Text_Ghost:
	.string "GHOST$"

CheatCode_Text_Steel:
	.string "STEEL$"

CheatCode_Text_Electric:
	.string "ELECTRIC$"

CheatCode_Text_Psychic:
	.string "PSYCHIC$"

CheatCode_Text_Ice:
	.string "ICE$"

CheatCode_Text_Dragon:
	.string "DRAGON$"

CheatCode_Text_Dark:
	.string "DARK$"

CheatCode_Text_Normal:
	.string "NORMAL$"

CheatCode_Text_Fairy:
	.string "FAIRY$"
