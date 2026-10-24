@ Crystal Imperium: milestone care packages from PROF. ELM.
@ src/care_packages.c starts EventScript_CarePackage on the player's next step after a milestone:
@ each Gym Badge and becoming Champion. VAR_CARE_PACKAGES counts the packages received; while
@ milestones are ahead of it, the next package arrives (so a save from an older build catches up
@ one package per step). Packages 1-8: Johto badges, 9: Champion, 10-17: Kanto badges.
@ Besides supplies they carry the evolution items found nowhere else in the game.
EventScript_CarePackage::
	lockall
	playse SE_EXP_MAX
	msgbox CarePackage_Text_Arrived, MSGBOX_DEFAULT
	switch VAR_CARE_PACKAGES
	case 0, CarePackage_1
	case 1, CarePackage_2
	case 2, CarePackage_3
	case 3, CarePackage_4
	case 4, CarePackage_5
	case 5, CarePackage_6
	case 6, CarePackage_7
	case 7, CarePackage_8
	case 8, CarePackage_9
	case 9, CarePackage_10
	case 10, CarePackage_11
	case 11, CarePackage_12
	case 12, CarePackage_13
	case 13, CarePackage_14
	case 14, CarePackage_15
	case 15, CarePackage_16
	case 16, CarePackage_17
	goto CarePackage_Done

CarePackage_1::
	giveitem ITEM_POKE_BALL, 10
	giveitem ITEM_GREAT_BALL, 5
	giveitem ITEM_SUPER_POTION, 5
	giveitem ITEM_LINKING_CORD
	giveitem ITEM_SWEET_APPLE
	giveitem ITEM_TART_APPLE
	goto CarePackage_Done

CarePackage_2::
	giveitem ITEM_GREAT_BALL, 10
	giveitem ITEM_REVIVE, 3
	giveitem ITEM_UPGRADE
	giveitem ITEM_SACHET
	giveitem ITEM_WHIPPED_DREAM
	giveitem ITEM_SYRUPY_APPLE
	goto CarePackage_Done

CarePackage_3::
	giveitem ITEM_ULTRA_BALL, 5
	giveitem ITEM_HYPER_POTION, 5
	giveitem ITEM_PRISM_SCALE
	giveitem ITEM_SUN_STONE, 3
	giveitem ITEM_LINKING_CORD
	goto CarePackage_Done

CarePackage_4::
	giveitem ITEM_ULTRA_BALL, 5
	giveitem ITEM_STRAWBERRY_SWEET
	giveitem ITEM_BERRY_SWEET
	giveitem ITEM_LOVE_SWEET
	giveitem ITEM_STAR_SWEET
	giveitem ITEM_CLOVER_SWEET
	giveitem ITEM_FLOWER_SWEET
	giveitem ITEM_RIBBON_SWEET
	goto CarePackage_Done

CarePackage_5::
	giveitem ITEM_FULL_HEAL, 5
	giveitem ITEM_MAX_REVIVE
	giveitem ITEM_CRACKED_POT
	giveitem ITEM_CHIPPED_POT
	giveitem ITEM_UNREMARKABLE_TEACUP
	giveitem ITEM_MASTERPIECE_TEACUP
	goto CarePackage_Done

CarePackage_6::
	giveitem ITEM_ULTRA_BALL, 10
	giveitem ITEM_PP_UP, 3
	giveitem ITEM_LEADERS_CREST
	giveitem ITEM_AUSPICIOUS_ARMOR
	giveitem ITEM_MALICIOUS_ARMOR
	goto CarePackage_Done

CarePackage_7::
	giveitem ITEM_MAX_POTION, 5
	giveitem ITEM_MAX_REVIVE, 2
	giveitem ITEM_METAL_ALLOY
	giveitem ITEM_LINKING_CORD
	goto CarePackage_Done

CarePackage_8::
	giveitem ITEM_FULL_RESTORE, 3
	giveitem ITEM_ABILITY_PATCH
	giveitem ITEM_GIMMIGHOUL_COIN, 999
	goto CarePackage_Done

CarePackage_9::
	goto_if_unset FLAG_SYS_GAME_CLEAR, CarePackage_9_Items
	msgbox CarePackage_Text_Champion, MSGBOX_DEFAULT
CarePackage_9_Items:
	giveitem ITEM_MASTER_BALL
	giveitem ITEM_PP_MAX, 3
	giveitem ITEM_SCROLL_OF_DARKNESS
	giveitem ITEM_SCROLL_OF_WATERS
	goto CarePackage_Done

CarePackage_10::
	giveitem ITEM_ULTRA_BALL, 10
	giveitem ITEM_FULL_RESTORE, 3
	giveitem ITEM_SUN_STONE, 3
	goto CarePackage_Done

CarePackage_11::
	giveitem ITEM_ULTRA_BALL, 10
	giveitem ITEM_MAX_REVIVE, 3
	giveitem ITEM_PP_MAX, 2
	goto CarePackage_Done

CarePackage_12::
	giveitem ITEM_QUICK_BALL, 10
	giveitem ITEM_FULL_RESTORE, 5
	goto CarePackage_Done

CarePackage_13::
	giveitem ITEM_DUSK_BALL, 10
	giveitem ITEM_MAX_ELIXIR, 3
	giveitem ITEM_ABILITY_PATCH
	goto CarePackage_Done

CarePackage_14::
	giveitem ITEM_ULTRA_BALL, 15
	giveitem ITEM_MAX_REVIVE, 3
	giveitem ITEM_PP_MAX, 2
	goto CarePackage_Done

CarePackage_15::
	giveitem ITEM_LUXURY_BALL, 10
	giveitem ITEM_FULL_RESTORE, 5
	giveitem ITEM_MAX_ELIXIR, 3
	goto CarePackage_Done

CarePackage_16::
	giveitem ITEM_MASTER_BALL
	giveitem ITEM_MAX_REVIVE, 5
	giveitem ITEM_FULL_RESTORE, 5
	goto CarePackage_Done

CarePackage_17::
	giveitem ITEM_MASTER_BALL
	giveitem ITEM_PP_MAX, 5
	giveitem ITEM_ABILITY_PATCH, 2
	goto CarePackage_Done

CarePackage_Done::
	addvar VAR_CARE_PACKAGES, 1
	releaseall
	end

CarePackage_Text_Arrived:
	.string "A care package from PROF. ELM\n"
	.string "arrived for your progress!$"

CarePackage_Text_Champion:
	.string "PROF. ELM: Congratulations,\n"
	.string "CHAMPION!\p"
	.string "Word is that rare and legendary {PKMN}\n"
	.string "now show up in the wild!$"
