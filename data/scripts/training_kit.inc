@ Crystal Imperium: Training Kit key item, also STATS in the L menu. Change a party Pokemon's nature
@ (any of the 25), cycle its ability through the species' abilities, including the Hidden Ability,
@ or edit its IVs and EVs (OpenStatEditor, Imperium's Stat Editor). Free and unlimited.
EventScript_TrainingKit::
	lockall
	message TrainingKit_Text_WhatToChange
	waitmessage
	dynmultichoice 18, 4, FALSE, 4, 0, DYN_MULTICHOICE_CB_NONE, TrainingKit_Text_OptNature, TrainingKit_Text_OptAbility, TrainingKit_Text_OptIvsEvs, TrainingKit_Text_OptCancel
	switch VAR_RESULT
	case 0, TrainingKit_EventScript_Nature
	case 1, TrainingKit_EventScript_Ability
	case 2, TrainingKit_EventScript_IvsEvs
	goto TrainingKit_EventScript_End

TrainingKit_EventScript_Nature::
	call TrainingKit_EventScript_ChooseMon
	message TrainingKit_Text_WhichNature
	waitmessage
	dynmultichoice 15, 0, FALSE, 6, 0, DYN_MULTICHOICE_CB_NONE, TrainingKit_Text_NatureHardy, TrainingKit_Text_NatureLonely, TrainingKit_Text_NatureBrave, TrainingKit_Text_NatureAdamant, TrainingKit_Text_NatureNaughty, TrainingKit_Text_NatureBold, TrainingKit_Text_NatureDocile, TrainingKit_Text_NatureRelaxed, TrainingKit_Text_NatureImpish, TrainingKit_Text_NatureLax, TrainingKit_Text_NatureTimid, TrainingKit_Text_NatureHasty, TrainingKit_Text_NatureSerious, TrainingKit_Text_NatureJolly, TrainingKit_Text_NatureNaive, TrainingKit_Text_NatureModest, TrainingKit_Text_NatureMild, TrainingKit_Text_NatureQuiet, TrainingKit_Text_NatureBashful, TrainingKit_Text_NatureRash, TrainingKit_Text_NatureCalm, TrainingKit_Text_NatureGentle, TrainingKit_Text_NatureSassy, TrainingKit_Text_NatureCareful, TrainingKit_Text_NatureQuirky
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, TrainingKit_EventScript_End
	copyvar VAR_0x8005, VAR_RESULT
	special TrainingKit_SetNature
	playse SE_SUCCESS
	msgbox TrainingKit_Text_NatureChanged, MSGBOX_DEFAULT
	goto TrainingKit_EventScript_End

TrainingKit_EventScript_Ability::
	call TrainingKit_EventScript_ChooseMon
	special TrainingKit_CycleAbility
	goto_if_eq VAR_RESULT, FALSE, TrainingKit_EventScript_OnlyOneAbility
	playse SE_SUCCESS
	msgbox TrainingKit_Text_AbilityChanged, MSGBOX_DEFAULT
	goto TrainingKit_EventScript_End

TrainingKit_EventScript_IvsEvs::
	call TrainingKit_EventScript_ChooseMon
	special OpenStatEditor
	waitstate
	goto TrainingKit_EventScript_End

TrainingKit_EventScript_OnlyOneAbility::
	msgbox TrainingKit_Text_OnlyOneAbility, MSGBOX_DEFAULT
	goto TrainingKit_EventScript_End

@ Returns with the party slot in VAR_0x8004, or ends the script if nothing (or an Egg) was chosen
TrainingKit_EventScript_ChooseMon::
	special ChoosePartyMon
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, TrainingKit_EventScript_End
	special IsSelectedMonEgg
	goto_if_eq VAR_RESULT, TRUE, TrainingKit_EventScript_Egg
	return

TrainingKit_EventScript_Egg::
	msgbox TrainingKit_Text_Egg, MSGBOX_DEFAULT
TrainingKit_EventScript_End::
	closemessage
	releaseall
	end

TrainingKit_Text_WhatToChange:
	.string "What would you like to change?$"
TrainingKit_Text_OptNature:
	.string "NATURE$"
TrainingKit_Text_OptAbility:
	.string "ABILITY$"
TrainingKit_Text_OptIvsEvs:
	.string "IVs & EVs$"
TrainingKit_Text_OptCancel:
	.string "CANCEL$"
TrainingKit_Text_WhichNature:
	.string "Choose a new nature.$"
TrainingKit_Text_NatureChanged:
	.string "{STR_VAR_1}'s nature is now\n{STR_VAR_2}!$"
TrainingKit_Text_AbilityChanged:
	.string "{STR_VAR_1}'s ability is now\n{STR_VAR_2}!$"
TrainingKit_Text_OnlyOneAbility:
	.string "{STR_VAR_1} only has one ability:\n{STR_VAR_2}.$"
TrainingKit_Text_Egg:
	.string "An EGG can't be changed.$"
TrainingKit_Text_NatureHardy:
	.string "HARDY$"
TrainingKit_Text_NatureLonely:
	.string "LONELY +ATK -DEF$"
TrainingKit_Text_NatureBrave:
	.string "BRAVE +ATK -SPE$"
TrainingKit_Text_NatureAdamant:
	.string "ADAMANT +ATK -SPA$"
TrainingKit_Text_NatureNaughty:
	.string "NAUGHTY +ATK -SPD$"
TrainingKit_Text_NatureBold:
	.string "BOLD +DEF -ATK$"
TrainingKit_Text_NatureDocile:
	.string "DOCILE$"
TrainingKit_Text_NatureRelaxed:
	.string "RELAXED +DEF -SPE$"
TrainingKit_Text_NatureImpish:
	.string "IMPISH +DEF -SPA$"
TrainingKit_Text_NatureLax:
	.string "LAX +DEF -SPD$"
TrainingKit_Text_NatureTimid:
	.string "TIMID +SPE -ATK$"
TrainingKit_Text_NatureHasty:
	.string "HASTY +SPE -DEF$"
TrainingKit_Text_NatureSerious:
	.string "SERIOUS$"
TrainingKit_Text_NatureJolly:
	.string "JOLLY +SPE -SPA$"
TrainingKit_Text_NatureNaive:
	.string "NAIVE +SPE -SPD$"
TrainingKit_Text_NatureModest:
	.string "MODEST +SPA -ATK$"
TrainingKit_Text_NatureMild:
	.string "MILD +SPA -DEF$"
TrainingKit_Text_NatureQuiet:
	.string "QUIET +SPA -SPE$"
TrainingKit_Text_NatureBashful:
	.string "BASHFUL$"
TrainingKit_Text_NatureRash:
	.string "RASH +SPA -SPD$"
TrainingKit_Text_NatureCalm:
	.string "CALM +SPD -ATK$"
TrainingKit_Text_NatureGentle:
	.string "GENTLE +SPD -DEF$"
TrainingKit_Text_NatureSassy:
	.string "SASSY +SPD -SPE$"
TrainingKit_Text_NatureCareful:
	.string "CAREFUL +SPD -SPA$"
TrainingKit_Text_NatureQuirky:
	.string "QUIRKY$"
