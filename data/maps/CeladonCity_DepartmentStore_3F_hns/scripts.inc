CeladonCity_DepartmentStore_3F_hns_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, CeladonDeptElevator_OnFrame
	.byte 0

CeladonDept3_EventScript_Youngster::
	msgbox CeladonDeptStore3F_Text_Youngster, MSGBOX_NPC
	end
CeladonDept3_EventScript_Gbakid1::
	msgbox CeladonDeptStore3F_Text_GameboyKid1, MSGBOX_NPC
	end
CeladonDept3_EventScript_Gbakid2::
	msgbox CeladonDeptStore3F_Text_GameboyKid2, MSGBOX_NPC
	end
CeladonDept3_EventScript_SuperNerd::
	msgbox CeladonDeptStore3F_Text_SuperNerd, MSGBOX_NPC
	end
@ Crystal Imperium: Heart & Soul's ten TMs here are among the TM shop's (EventScript_TMShop,
@ data/scripts/tm_shop_hns.inc), the one every Poke Mart's TM clerk has: all of them by now.
CeladonDept3_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	call EventScript_TMShop
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CeladonDept3_EventScript_Directory::
	msgbox CeladonDeptStore3F_Text_Directory, MSGBOX_SIGN
	end

CeladonDeptStore3F_Text_Youngster:
	.string "I can't decide which POKéMON I\n"
	.string "should use this TM on…$"

CeladonDeptStore3F_Text_GameboyKid1:
	.string "Uh-oh! I traded my POKéMON without\n"
	.string "removing the UPGRADE from it.$"

CeladonDeptStore3F_Text_GameboyKid2:
	.string "Yeah! I'm finally getting a\n"
	.string "PORYGON!\p"
	.string "I'm no good at the slots, so I\n"
	.string "could never get enough coins…\p"
	.string "…Huh?\p"
	.string "The traded PORYGON turned into a\n"
	.string "different POKéMON!$"

CeladonDeptStore3F_Text_SuperNerd:
	.string "The TM SHOP sells some rare moves.$"

CeladonDeptStore3F_Text_Directory:
	.string "3F: TM SHOP\p"
	.string "Make Your POKéMON Stronger!$"

