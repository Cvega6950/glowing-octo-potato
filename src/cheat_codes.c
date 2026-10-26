// Crystal Imperium: Emerald Imperium's cheat codes (DECISIONS.md D37), typed at the NES in the
// player's room (data/scripts/cheat_codes.inc), in any case and with or without spaces.
#include "global.h"
#include "cheat_codes.h"
#include "event_data.h"
#include "item.h"
#include "money.h"
#include "pokedex.h"
#include "roamer.h"
#include "script.h"
#include "string_util.h"
#include "constants/characters.h"
#include "constants/cheat_codes.h"
#include "constants/flags.h"
#include "constants/items.h"
#include "constants/pokedex.h"
#include "constants/pokemon.h"
#include "constants/species.h"
#include "constants/vars.h"

// The Mega Specialist's full stock on Goldenrod Dept. Store 5F: every Mega Stone this game's Megas use
extern const u16 GoldenrodDeptStore5_MegaStones4[];

// Imperium's codes and their aliases
static const struct
{
    const u8 *text;
    u8 code;
} sCheatCodes[] =
{
    { COMPOUND_STRING("DEXALL"),    CHEAT_CODE_DEXALL },
    { COMPOUND_STRING("DXA"),       CHEAT_CODE_DEXALL },
    { COMPOUND_STRING("CAUGHTALL"), CHEAT_CODE_CAUGHTALL },
    { COMPOUND_STRING("CAL"),       CHEAT_CODE_CAUGHTALL },
    { COMPOUND_STRING("EZCATCH"),   CHEAT_CODE_EZCATCH },
    { COMPOUND_STRING("EZC"),       CHEAT_CODE_EZCATCH },
    { COMPOUND_STRING("MEGA"),      CHEAT_CODE_MEGA },
    { COMPOUND_STRING("SHINYS"),    CHEAT_CODE_SHINYS },
    { COMPOUND_STRING("SHS"),       CHEAT_CODE_SHINYS },
    { COMPOUND_STRING("MAXMONEY"),  CHEAT_CODE_MAXMONEY },
    { COMPOUND_STRING("MMY"),       CHEAT_CODE_MAXMONEY },
    { COMPOUND_STRING("MONO"),      CHEAT_CODE_MONO },
    { COMPOUND_STRING("SHINYR"),    CHEAT_CODE_SHINYR },
    { COMPOUND_STRING("SHR"),       CHEAT_CODE_SHINYR },
};

// The MONO code's types, in its menu's order, and PROF. ELM's three Pokemon for each (Emerald
// Imperium's lists; Fire, Water and Grass have no list there either)
static const u8 sMonoStarterTypes[MONO_STARTER_TYPE_COUNT] =
{
    TYPE_FIGHTING, TYPE_FLYING, TYPE_POISON, TYPE_GROUND, TYPE_ROCK, TYPE_BUG, TYPE_GHOST, TYPE_STEEL,
    TYPE_ELECTRIC, TYPE_PSYCHIC, TYPE_ICE, TYPE_DRAGON, TYPE_DARK, TYPE_NORMAL, TYPE_FAIRY,
};

static const u16 sMonoStarters[MONO_STARTER_TYPE_COUNT][3] =
{
    { SPECIES_MANKEY,    SPECIES_MACHOP,          SPECIES_TIMBURR },
    { SPECIES_HOPPIP,    SPECIES_FLETCHLING,      SPECIES_ROOKIDEE },
    { SPECIES_BUDEW,     SPECIES_VENIPEDE,        SPECIES_KOFFING },
    { SPECIES_TRAPINCH,  SPECIES_GEODUDE,         SPECIES_TYMPOLE },
    { SPECIES_ROLYCOLY,  SPECIES_GEODUDE_ALOLA,   SPECIES_NACLI },
    { SPECIES_GRUBBIN,   SPECIES_BLIPBUG,         SPECIES_SCATTERBUG },
    { SPECIES_GASTLY,    SPECIES_LITWICK,         SPECIES_DUSKULL },
    { SPECIES_TINKATINK, SPECIES_HONEDGE,         SPECIES_KLINK },
    { SPECIES_PICHU,     SPECIES_SHINX,           SPECIES_MAREEP },
    { SPECIES_HATENNA,   SPECIES_SOLOSIS,         SPECIES_GOTHITA },
    { SPECIES_SNOVER,    SPECIES_SWINUB,          SPECIES_SPHEAL },
    { SPECIES_BAGON,     SPECIES_GIBLE,           SPECIES_DRATINI },
    { SPECIES_PAWNIARD,  SPECIES_ZIGZAGOON_GALAR, SPECIES_SANDILE },
    { SPECIES_WHISMUR,   SPECIES_LILLIPUP,        SPECIES_SMOLIV },
    { SPECIES_COTTONEE,  SPECIES_IGGLYBUFF,       SPECIES_IMPIDIMP },
};

// callnative: VAR_RESULT = the code EnterCode put in gStringVar2, CHEAT_CODE_NONE if it is none
void CheatCode_Find(struct ScriptContext *ctx)
{
    u8 code[CODE_NAME_LENGTH + 1];
    u32 i, length = 0;

    for (i = 0; gStringVar2[i] != EOS && length < CODE_NAME_LENGTH; i++)
    {
        u8 c = gStringVar2[i];

        if (c == CHAR_SPACE)
            continue;
        if (c >= CHAR_a && c <= CHAR_z)
            c = c - CHAR_a + CHAR_A;
        code[length++] = c;
    }
    code[length] = EOS;

    gSpecialVar_Result = CHEAT_CODE_NONE;
    for (i = 0; i < ARRAY_COUNT(sCheatCodes); i++)
    {
        if (StringCompare(code, sCheatCodes[i].text) == 0)
        {
            gSpecialVar_Result = sCheatCodes[i].code;
            break;
        }
    }
}

// callnative, CAUGHTALL: every Pokemon seen and caught in the Pokedex, which goes National
void CheatCode_MarkAllCaught(struct ScriptContext *ctx)
{
    u32 i;

    for (i = NATIONAL_DEX_NONE + 1; i <= NATIONAL_DEX_COUNT; i++)
    {
        GetSetPokedexFlag(i, FLAG_SET_SEEN);
        GetSetPokedexFlag(i, FLAG_SET_CAUGHT);
    }
    EnableNationalPokedex();
}

// callnative, EZCATCH: switches EASY CATCH (the Features tab's first row); VAR_RESULT = TRUE if now on
void CheatCode_ToggleEasyCatch(struct ScriptContext *ctx)
{
    gSaveBlock3Ptr->challengeSettings.tx_Features_EasyCatchOff = !gSaveBlock3Ptr->challengeSettings.tx_Features_EasyCatchOff;
    gSpecialVar_Result = !gSaveBlock3Ptr->challengeSettings.tx_Features_EasyCatchOff;
}

// callnative, MEGA: the Mega Ring if the player hasn't got it (VAR_0x8006 = TRUE then), and one of
// each Mega Stone they haven't got in the Bag or the PC, to the Bag or else the PC. VAR_0x8005 = the
// stones given, VAR_RESULT = the stones left out for lack of room (entering MEGA again brings them).
void CheatCode_GiveMegaStones(struct ScriptContext *ctx)
{
    const u16 *stone;

    gSpecialVar_0x8005 = 0;
    gSpecialVar_0x8006 = FALSE;
    gSpecialVar_Result = 0;
    if (!CheckBagHasItem(ITEM_MEGA_RING, 1) && AddBagItem(ITEM_MEGA_RING, 1))
    {
        FlagSet(FLAG_RECEIVED_MEGA_RING);
        gSpecialVar_0x8006 = TRUE;
    }
    for (stone = GoldenrodDeptStore5_MegaStones4; *stone != ITEM_NONE; stone++)
    {
        if (CheckBagHasItem(*stone, 1) || CheckPCHasItem(*stone, 1))
            continue;
        if (AddBagItem(*stone, 1) || AddPCItem(*stone, 1))
            gSpecialVar_0x8005++;
        else
            gSpecialVar_Result++;
    }
}

// callnative, MAXMONEY
void CheatCode_SetMaxMoney(struct ScriptContext *ctx)
{
    SetMoney(&gSaveBlock1Ptr->money, MAX_MONEY);
}

// callnative, SHINYR: the roaming Pokemon shiny, those roaming now and those to come
void CheatCode_MakeRoamersShiny(struct ScriptContext *ctx)
{
    FlagSet(FLAG_CODE_SHINY_ROAMERS);
    SetRoamersShiny();
}

// callnative, MONO: VAR_MONO_STARTER_TYPE from the menu's choice in VAR_RESULT (0: off, then the types)
void CheatCode_SetMonoType(struct ScriptContext *ctx)
{
    u32 choice = gSpecialVar_Result;

    if (choice >= 1 && choice <= MONO_STARTER_TYPE_COUNT)
        VarSet(VAR_MONO_STARTER_TYPE, sMonoStarterTypes[choice - 1]);
    else
        VarSet(VAR_MONO_STARTER_TYPE, TYPE_NONE);
}

// callnative (PROF. ELM's lab): VAR_RESULT = the Pokemon in Poke Ball VAR_STARTER_MON (0-2): the
// Johto starters, or the MONO code's type's three
void GetLabStarterSpecies(struct ScriptContext *ctx)
{
    static const u16 sJohtoStarters[] = { SPECIES_CHIKORITA, SPECIES_CYNDAQUIL, SPECIES_TOTODILE };
    u32 ball = VarGet(VAR_STARTER_MON) % ARRAY_COUNT(sJohtoStarters);
    u32 type = VarGet(VAR_MONO_STARTER_TYPE);
    u32 i;

    gSpecialVar_Result = sJohtoStarters[ball];
    for (i = 0; i < MONO_STARTER_TYPE_COUNT; i++)
    {
        if (type != TYPE_NONE && sMonoStarterTypes[i] == type)
            gSpecialVar_Result = sMonoStarters[i][ball];
    }
}
