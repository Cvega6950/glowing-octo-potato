#ifndef GUARD_CONSTANTS_CARE_PACKAGES_H
#define GUARD_CONSTANTS_CARE_PACKAGES_H

// Crystal Imperium care packages (src/care_packages.c, data/scripts/care_packages.inc): how
// EventScript_CarePackage was started, in VAR_0x8006
#define CARE_PACKAGE_NEW     0 // a package that has just arrived
#define CARE_PACKAGE_UPDATE  1 // an earlier package's 0.12.0 contents, for a save from before 0.12.0
#define CARE_PACKAGE_RESUME  2 // the rest of a package that stopped because the BAG and PC were full
#define CARE_PACKAGE_TMS     3 // the TMs of the packages a save from before 0.15.1 had already received
#define CARE_PACKAGE_PP_MAX  4 // PP Max up to 999, once, for a save whose starting package came before 0.15.2

// Milestone packages: one per Gym Badge and one for becoming Champion; package 0 comes at the start
#define CARE_PACKAGE_COUNT   17

// The TMs come with the starting package (tier 0, the ones the TM shops sell from the start) and the
// first eight milestone packages (tier k, the ones they sell from k badges on): DECISIONS.md D48
#define CARE_PACKAGE_TM_TIERS 9

#endif // GUARD_CONSTANTS_CARE_PACKAGES_H
