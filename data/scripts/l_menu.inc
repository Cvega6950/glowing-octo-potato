@ Crystal Imperium: the L menu's messages (src/l_menu.c)
LMenu_EventScript_PokeVial::
	lockall
	msgbox LMenu_Text_PokeVialHealed, MSGBOX_DEFAULT
	releaseall
	end

LMenu_EventScript_NoDexNav::
	lockall
	msgbox LMenu_Text_NoDexNav, MSGBOX_DEFAULT
	releaseall
	end

LMenu_Text_PokeVialHealed:
	.string "Your {PKMN} were fully healed!$"

LMenu_Text_NoDexNav:
	.string "No wild POKéMON live here.$"
