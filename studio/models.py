"""Strict authoring contracts. Game data is declarative; no executable user scripts."""
from __future__ import annotations
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{1,63}$")]
Colour = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]
Kind = Literal["characters", "factions", "missions", "assets"]
Power = Literal["web-step", "borrowed-voice", "trick-mirror"]
class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

class Variant(Strict):
    id: Identifier
    label: str = Field(min_length=1, max_length=100)
    body_asset_id: Identifier | None = None
    animation_asset_id: Identifier | None = None
    cloth_colour: Colour = "#B16D38"
    accent_colour: Colour = "#DCC482"
    body_scale: float = Field(default=1, ge=0.8, le=1.2)
    morph_targets: dict[str, float] = Field(default_factory=dict, max_length=16)
    @field_validator("morph_targets")
    @classmethod
    def check_morphs(cls, value):
        import math, re
        if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", k) or not math.isfinite(v) or not 0 <= v <= 1 for k,v in value.items()):
            raise ValueError("Morph names must be identifiers and values finite in [0,1].")
        return value

class Character(Strict):
    name: str = Field(min_length=1,max_length=120)
    role: str = Field(min_length=1,max_length=160)
    description: str = Field(default="",max_length=12000)
    archetype: str = Field(default="original",max_length=200)
    representation: Literal["human","spirit","animal","collective","mythic"] = "human"
    silhouette: Literal["courier","scholar","guard","serpent","swarm","spirit","court"] = "courier"
    faction_ids: list[Identifier] = Field(default_factory=list,max_length=10)
    powers: list[Power] = Field(default_factory=list,max_length=3)
    variants: list[Variant] = Field(min_length=1,max_length=20)
    source_note: str = Field(min_length=1,max_length=2000)
    culture_review_required: bool = True
    in_vertical_slice: bool = False
    stage: Literal["concept","greybox","art-in-progress","runtime-ready"] = "concept"
    @field_validator("variants")
    @classmethod
    def distinct_variants(cls,value):
        if len({v.id for v in value}) != len(value):
            raise ValueError("Variant IDs must be unique within a character.")
        return value
    @field_validator("faction_ids","powers")
    @classmethod
    def distinct_ids(cls,value):
        if len(set(value)) != len(value): raise ValueError("Duplicate IDs are not allowed.")
        return value

class Faction(Strict):
    name: str = Field(min_length=1,max_length=120)
    description: str = Field(default="",max_length=5000)
    public_goal: str = Field(default="",max_length=500)
    private_pressure: str = Field(default="",max_length=500)

class Mission(Strict):
    name: str = Field(min_length=1,max_length=120)
    description: str = Field(default="",max_length=12000)
    character_ids: list[Identifier] = Field(default_factory=list,max_length=30)
    faction_ids: list[Identifier] = Field(default_factory=list,max_length=10)
    estimated_minutes: int = Field(default=15,ge=1,le=120)
    supported_routes: list[Literal["social","negotiation","rooftop"]] = Field(min_length=1,max_length=3)
    endings: list[str] = Field(min_length=2,max_length=8)

class LeopardVisualDesign(Strict):
    """Cosmetic binding independent of narrative Osebo and collision scale."""
    design_id: Literal["osebo-leopard-v1"]
    skeleton_key: Literal["osebo-feline-biped-v001"]
    definition_path: Literal["/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard"]
    source_revision: Identifier
    source_glb_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    cape_colour: Colour = "#752433"
    accent_colour: Colour = "#C29848"

STORY_DESIGNS = {
    "kwaku-human-v1": ("Kwaku", "authored-v002"),
    "aso-yaa-human-v1": ("AsoYaa", "authored-v001"),
    "esi-human-v1": ("EsiHuman", "authored-v001"),
    "osebo-human-v1": ("OseboHuman", "authored-v001"),
    "kojo-tortoise-v1": ("KojoTortoise", "authored-v001"),
    "kofi-hornbill-v1": ("KofiHornbill", "authored-v001"),
    "esi-moth-v1": ("EsiMoth", "authored-v001"),
}

STORY_REFINEMENTS = {
    ("aso-yaa-human-v1", "authored-v007"): {
        "definition": "/Game/Ananse/Characters/AsoYaa/Negotiation_v002/DA_AsoYaa.DA_AsoYaa",
        "mesh": "/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa",
        "folder": "Authored_v007",
    },
    ("aso-yaa-human-v1", "authored-v004"): {
        "definition": "/Game/Ananse/Characters/AsoYaa/Negotiation_v001/DA_AsoYaa.DA_AsoYaa",
        "mesh": "/Game/Ananse/Characters/AsoYaa/Negotiation_v001/AsoYaa.AsoYaa",
        "folder": "Authored_v004",
    },
    ("kwaku-human-v1", "authored-v016"): {
        "definition": "/Game/Ananse/Characters/Kwaku/Interactions_v005/DA_Kwaku.DA_Kwaku",
        "mesh": "/Game/Ananse/Characters/Kwaku/Interactions_v005/Kwaku.Kwaku",
        "folder": "Authored_v016",
    },
    ("kwaku-human-v1", "authored-v015"): {
        "definition": "/Game/Ananse/Characters/Kwaku/Interactions_v003/DA_Kwaku.DA_Kwaku",
        "mesh": "/Game/Ananse/Characters/Kwaku/Interactions_v003/Kwaku.Kwaku",
        "folder": "Authored_v015",
    },
    ("kwaku-human-v1", "authored-v008"): {
        "definition": "/Game/Ananse/Characters/Kwaku/Refined_v002/DA_Kwaku.DA_Kwaku",
        "mesh": "/Game/Ananse/Characters/Kwaku/Refined_v002/Kwaku.Kwaku",
        "folder": "Authored_v008",
    },
    ("kwaku-human-v1", "authored-v006"): {
        "definition": "/Game/Ananse/Characters/Kwaku/Refined_v001/DA_Kwaku.DA_Kwaku",
        "mesh": "/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku.Kwaku",
        "folder": "Authored_v006",
    },
}

class StoryVisualDesign(Strict):
    design_id: Literal["kwaku-human-v1", "aso-yaa-human-v1", "esi-human-v1", "osebo-human-v1", "kojo-tortoise-v1", "kofi-hornbill-v1", "esi-moth-v1"]
    skeleton_key: str
    definition_path: str
    source_revision: Identifier
    source_glb_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    @model_validator(mode="after")
    def fixed_binding(self):
        key, revision = STORY_DESIGNS[self.design_id]
        refined = STORY_REFINEMENTS.get((self.design_id, self.source_revision))
        expected = refined["definition"] if refined else f"/Game/Ananse/Characters/{key}/Story_v001/DA_{key}.DA_{key}"
        if self.skeleton_key != key+"-independent-v001" or self.definition_path != expected or (not refined and self.source_revision != revision):
            raise ValueError("Story design requires its own allowlisted skeleton, definition and source revision.")
        return self

class Asset(Strict):
    name: str = Field(min_length=1,max_length=120)
    category: Literal["skeletal-mesh","static-mesh","animation","material","texture","audio"]
    unreal_path: str = Field(default="",max_length=400)
    source_creator: str = Field(default="",max_length=300)
    source_reference: str = Field(default="",max_length=2000)
    licence: str = Field(default="UNVERIFIED",max_length=1000)
    sha256: str = Field(default="",pattern=r"^$|^[a-f0-9]{64}$")
    triangles_lod0: int = Field(default=0,ge=0,le=10000000)
    material_slots: int = Field(default=1,ge=1,le=32)
    mobile_review_passed: bool = False
    visual_design: LeopardVisualDesign | StoryVisualDesign | None = None
    @model_validator(mode="after")
    def visual_binding_matches_mesh(self):
        expected = "/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard"
        if self.visual_design and self.visual_design.design_id in STORY_DESIGNS:
            key = STORY_DESIGNS[self.visual_design.design_id][0]
            refined = STORY_REFINEMENTS.get((self.visual_design.design_id, self.visual_design.source_revision))
            expected = refined["mesh"] if refined else f"/Game/Ananse/Characters/{key}/Story_v001/{key}.{key}"
        if self.visual_design and (self.category != "skeletal-mesh" or self.unreal_path != expected):
            raise ValueError("Visual revisions require the allowlisted design mesh; no narrative or skeleton substitution.")
        return self
    status: Literal["planned","quarantine","review","approved"] = "planned"
    @field_validator("unreal_path")
    @classmethod
    def valid_unreal_path(cls,value):
        import re
        if value and not re.fullmatch(r"/Game/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+\.[A-Za-z0-9_]+",value):
            raise ValueError("Use an Unreal soft object path under /Game; external URLs and traversal are forbidden.")
        return value

SCHEMAS={"characters":Character,"factions":Faction,"missions":Mission,"assets":Asset}

def validate(kind: str, data: dict) -> dict:
    return SCHEMAS[kind].model_validate(data).model_dump(mode="json")

def references(kind: str, data: dict) -> list[tuple[str,str]]:
    refs=[]
    if kind == "characters":
        refs += [("factions",x) for x in data["faction_ids"]]
        for v in data["variants"]:
            for key in ("body_asset_id","animation_asset_id"):
                if v.get(key): refs.append(("assets",v[key]))
    elif kind == "missions":
        refs += [("characters",x) for x in data["character_ids"]]
        refs += [("factions",x) for x in data["faction_ids"]]
    return refs

class CreateRecord(Strict):
    id: Identifier
    data: dict
class UpdateRecord(Strict):
    data: dict
class Review(Strict):
    version: int = Field(ge=1)
    decision: Literal["approved","rejected"]
    note: str = Field(min_length=8,max_length=3000)
class Publish(Strict):
    channel: Literal["prototype","production"] = "prototype"
class Revert(Strict):
    revision: int = Field(ge=1)
class LabAction(Strict):
    expected_version: int = Field(ge=1)
    action: str = Field(min_length=1,max_length=60)
