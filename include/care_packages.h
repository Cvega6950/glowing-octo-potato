#ifndef GUARD_CARE_PACKAGES_H
#define GUARD_CARE_PACKAGES_H

struct ScriptContext;

enum ItemDestination
{
    ITEM_NOWHERE,
    ITEM_TO_BAG,
    ITEM_TO_PC,
};

enum ItemDestination AddItemToBagOrPC(u16 itemId, u16 quantity);

bool32 TryStartCarePackageScript(void);
void CarePackage_LoadIntroText(struct ScriptContext *ctx);
void CarePackage_LoadContentsText(struct ScriptContext *ctx);
void CarePackage_GiveItems(struct ScriptContext *ctx);

#endif // GUARD_CARE_PACKAGES_H
