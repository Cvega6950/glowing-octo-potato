VioletCity_Mart_hns_MapScripts::
	.byte 0

VioletCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart 0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

@ Crystal Imperium: a TM clerk, Emerald Imperium-style (its first TM vendors, after its first Gym).
@ From the Zephyr Badge on, seven TMs at ¥100 each; the list is data/scripts/tm_shop_hns.inc
@ (tools/crystal_imperium/tm_list.py). The first time, the clerk also gives the four TMs Emerald
@ Imperium gives away before its second Gym (Bullet Seed, Bulldoze, Bug Bite, Stomping Tantrum).
VioletCity_Mart_EventScript_TMClerk::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE01_GET, VioletCity_Mart_EventScript_TMClerkNoBadge
	goto_if_set FLAG_RECEIVED_VIOLET_TMS, VioletCity_Mart_EventScript_TMClerkShop
	msgbox VioletCity_Mart_Text_TMClerkGift, MSGBOX_DEFAULT
	additem ITEM_TM_BULLET_SEED
	additem ITEM_TM_BULLDOZE
	additem ITEM_TM_BUG_BITE
	additem ITEM_TM_STOMPING_TANTRUM
	setflag FLAG_RECEIVED_VIOLET_TMS
	playfanfare MUS_OBTAIN_TMHM
	message VioletCity_Mart_Text_TMClerkGiftReceived
	waitmessage
	waitfanfare
	waitbuttonpress
VioletCity_Mart_EventScript_TMClerkShop::
	message VioletCity_Mart_Text_TMClerk
	waitmessage
	pokemart VioletCity_Mart_TMs
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

VioletCity_Mart_EventScript_TMClerkNoBadge::
	msgbox VioletCity_Mart_Text_TMClerkNoBadge, MSGBOX_DEFAULT
	release
	end

VioletCity_Mart_EventScript_Granny::
	lock
	faceplayer
	msgbox VioletCity_Mart_Text_Granny, MSGBOX_DEFAULT
	closemessage
	release
	end

VioletCity_Mart_EventScript_Rocker::
	lock
	faceplayer
	msgbox VioletCity_Mart_Text_CooltrainerM, MSGBOX_DEFAULT
	closemessage
	release
	end
	
VioletCity_Mart_Text_Granny:
	.string "When you first catch a POKéMON,\n"
	.string "it may be weak.\p"
	.string "But it will eventually grow to\n"
	.string "be strong.\p"
	.string "It's important to treat POKéMON\n"
	.string "with love.$"

VioletCity_Mart_Text_CooltrainerM:
	.string "POKéMON can hold items like\n"
	.string "POTION and ANTIDOTE.\p"
	.string "But they don't appear to know\n"
	.string "how to use man-made items.$"

VioletCity_Mart_Text_TMClerk:
	.string "Welcome! This counter sells TMs to\n"
	.string "TRAINERS with a GYM BADGE.\p"
	.string "Every TM is ¥100!$"

VioletCity_Mart_Text_TMClerkGift:
	.string "Oh! You have the ZEPHYRBADGE!\p"
	.string "Here, a few TMs on the house\n"
	.string "for a new GYM BADGE holder.$"

VioletCity_Mart_Text_TMClerkGiftReceived:
	.string "{PLAYER} received TM09 BULLET SEED,\n"
	.string "TM96 BULLDOZE, TM109 BUG BITE and\l"
	.string "TM110 STOMPING TANTRUM!$"

VioletCity_Mart_Text_TMClerkNoBadge:
	.string "This counter sells TMs to TRAINERS\n"
	.string "with a GYM BADGE.\p"
	.string "FALKNER at the GYM gives out the\n"
	.string "ZEPHYRBADGE. Come back with it!$"
