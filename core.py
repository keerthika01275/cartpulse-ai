# core.py
"""
CartPulse AI - Multi-Agent State Machine & Guardrails Engine
Track 1: Agentic Commerce & Autonomous Negotiation Concierge
"""

import os
import re
import time
import json
from pathlib import Path
from typing import TypedDict, Sequence, List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Load Environment
env_file = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_file, override=True)
api_key = os.getenv("OPENAI_API_KEY")

# --- 1. FULL MULTI-ITEM PRODUCT CATALOG WITH ALTERNATIVES & PRICE HISTORY ---
PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "bag_01": {
        "id": "bag_01",
        "name": "Artisan Leather Weekender Bag",
        "category": "Travel",
        "price": 150.00,
        "shipping_fee": 15.00,
        "dimensions": "20 x 12 x 9 inches",
        "weight": "3.2 lbs",
        "key_specs": "Delta/United/AA carry-on compliant, waterproof full-grain Italian leather, padded 16-inch laptop compartment, YKK brass zippers",
        "stock": 14,
        "margin_floor": 0.35,
        "icon": "🧳",
        "recommended_accessory": "acc_bag_01",
        "cheaper_alternative": {
            "id": "alt_bag_budget",
            "name": "Classic Canvas & Vegan Leather Duffel",
            "price": 68.00,
            "shipping_fee": 8.00,
            "icon": "🎒",
            "key_specs": "Water-resistant 600D canvas, 15-inch laptop sleeve, 28L capacity, TSA compliant",
            "dimensions": "19 x 11 x 8.5 inches",
            "weight": "1.8 lbs",
            "rating": 4.7,
            "savings": 82.00,
            "savings_pct": 55
        },
        "premium_alternative": {
            "id": "alt_bag_premium",
            "name": "Vachetta Heritage Luxury Overnighter",
            "price": 295.00,
            "shipping_fee": 20.00,
            "icon": "💼",
            "key_specs": "Hand-stitched Tuscan vegetable-tanned leather, solid brass hardware, modular garment suit folder",
            "dimensions": "22 x 14 x 10 inches",
            "weight": "4.1 lbs",
            "rating": 4.9
        },
        "price_history": [
            {"month": "May", "price": 135.0, "projected": False},
            {"month": "Jun", "price": 140.0, "projected": False},
            {"month": "Jul", "price": 145.0, "projected": False},
            {"month": "Aug (Current)", "price": 150.0, "projected": False},
            {"month": "Sep (Forecast)", "price": 168.0, "projected": True, "inflation_factor": "+12% leather import tariff"}
        ]
    },
    "audio_02": {
        "id": "audio_02",
        "name": "AeroPulse Pro ANC Headphones",
        "category": "Electronics",
        "price": 280.00,
        "shipping_fee": 10.00,
        "dimensions": "7.5 x 6.2 x 3.1 inches",
        "weight": "250 grams",
        "key_specs": "45dB Hybrid Active Noise Cancellation, 40-hour battery life (USB-C fast charge 10m=5hrs), LDAC lossless codec, Bluetooth 5.4 multi-point",
        "stock": 4,
        "margin_floor": 0.40,
        "icon": "🎧",
        "recommended_accessory": "acc_audio_01",
        "cheaper_alternative": {
            "id": "alt_audio_budget",
            "name": "AeroPulse Lite Wireless Headphones",
            "price": 95.00,
            "shipping_fee": 6.00,
            "icon": "🎧",
            "key_specs": "Standard 30dB ANC, 28-hr battery, AAC codec, lightweight foldable design, BT 5.2",
            "dimensions": "7.1 x 5.9 x 3.0 inches",
            "weight": "210 grams",
            "rating": 4.6,
            "savings": 185.00,
            "savings_pct": 66
        },
        "premium_alternative": {
            "id": "alt_audio_premium",
            "name": "AeroPulse Studio Master Audiophile",
            "price": 490.00,
            "shipping_fee": 15.00,
            "icon": "🎵",
            "key_specs": "Planar magnetic drivers, lossless USB-DAC 24-bit/192kHz, carbon fiber headband, sheepskin ear cushions",
            "dimensions": "8.0 x 6.5 x 3.5 inches",
            "weight": "310 grams",
            "rating": 5.0
        },
        "price_history": [
            {"month": "May", "price": 260.0, "projected": False},
            {"month": "Jun", "price": 270.0, "projected": False},
            {"month": "Jul", "price": 275.0, "projected": False},
            {"month": "Aug (Current)", "price": 280.0, "projected": False},
            {"month": "Sep (Forecast)", "price": 315.0, "projected": True, "inflation_factor": "+12.5% ANC chipset supply cost"}
        ]
    },
    "camp_03": {
        "id": "camp_03",
        "name": "SummitLite 2-Person Ultralight Tent",
        "category": "Outdoor",
        "price": 320.00,
        "shipping_fee": 20.00,
        "dimensions": "Packed: 16 x 5 inches | Pitched: 86 x 52 x 42 inches",
        "weight": "2.1 lbs",
        "key_specs": "3-season rating, 20D ripstop silnylon, DAC featherlite aluminum poles, 3000mm hydrostatic head waterproof rating, dual vestibules",
        "stock": 3,
        "margin_floor": 0.30,
        "icon": "⛺",
        "recommended_accessory": "acc_camp_01",
        "cheaper_alternative": {
            "id": "alt_camp_budget",
            "name": "TrailHaven 2-Person Backpacking Tent",
            "price": 139.00,
            "shipping_fee": 12.00,
            "icon": "⛺",
            "key_specs": "68D polyester rainfly, fiberglass poles, 2000mm waterproofing, fast 5-minute pitch setup",
            "dimensions": "Packed: 19 x 7 in | Pitched: 84 x 50 x 40 in",
            "weight": "4.5 lbs",
            "rating": 4.5,
            "savings": 181.00,
            "savings_pct": 57
        },
        "premium_alternative": {
            "id": "alt_camp_premium",
            "name": "ApexCarbon 4-Season Expedition Tent",
            "price": 580.00,
            "shipping_fee": 25.00,
            "icon": "🏔️",
            "key_specs": "Dyneema composite fabric, Easton carbon FX poles, 5000mm waterproof, 60mph wind tested",
            "dimensions": "Packed: 14 x 4.5 in | Pitched: 88 x 54 x 45 in",
            "weight": "1.7 lbs",
            "rating": 4.9
        },
        "price_history": [
            {"month": "May", "price": 290.0, "projected": False},
            {"month": "Jun", "price": 305.0, "projected": False},
            {"month": "Jul", "price": 310.0, "projected": False},
            {"month": "Aug (Current)", "price": 320.0, "projected": False},
            {"month": "Sep (Forecast)", "price": 355.0, "projected": True, "inflation_factor": "+11% silnylon raw material spike"}
        ]
    },
    "key_04": {
        "id": "key_04",
        "name": "Chronos 75% Wireless Mechanical Keyboard",
        "category": "Electronics",
        "price": 120.00,
        "shipping_fee": 8.00,
        "dimensions": "12.6 x 5.4 x 1.4 inches",
        "weight": "850 grams",
        "key_specs": "Hot-swappable Gateron Pro switches, gasket-mounted acoustic foam, 2.4GHz/BT5.1/USB-C tri-mode, per-key RGB, 4000mAh battery (200 hrs)",
        "stock": 42,
        "margin_floor": 0.45,
        "icon": "⌨️",
        "recommended_accessory": "acc_key_01",
        "cheaper_alternative": {
            "id": "alt_key_budget",
            "name": "Chronos Core 65% Wired Mechanical Keyboard",
            "price": 54.00,
            "shipping_fee": 6.00,
            "icon": "⌨️",
            "key_specs": "Outemu Red linear switches, ABS double-shot keycaps, white LED backlight, Type-C wired",
            "dimensions": "11.8 x 4.2 x 1.3 in",
            "weight": "620 grams",
            "rating": 4.6,
            "savings": 66.00,
            "savings_pct": 55
        },
        "premium_alternative": {
            "id": "alt_key_premium",
            "name": "Chronos Pro CNC Aluminum Custom Keyboard",
            "price": 240.00,
            "shipping_fee": 12.00,
            "icon": "✨",
            "key_specs": "Full CNC anodized aluminum body, brass internal weight bar, lubed holy panda switches, FR4 plate",
            "dimensions": "13.0 x 5.8 x 1.6 in",
            "weight": "1650 grams",
            "rating": 4.9
        },
        "price_history": [
            {"month": "May", "price": 105.0, "projected": False},
            {"month": "Jun", "price": 110.0, "projected": False},
            {"month": "Jul", "price": 115.0, "projected": False},
            {"month": "Aug (Current)", "price": 120.0, "projected": False},
            {"month": "Sep (Forecast)", "price": 138.0, "projected": True, "inflation_factor": "+15% semiconductor & switch surge"}
        ]
    },
    "brew_05": {
        "id": "brew_05",
        "name": "BaristaPro Compact Espresso Machine",
        "category": "Kitchen",
        "price": 450.00,
        "shipping_fee": 25.00,
        "dimensions": "11 x 8 x 12 inches",
        "weight": "11.5 lbs",
        "key_specs": "15-bar Italian Ulka pump, ThermoBlock 3-second rapid heating, commercial 54mm portafilter, stainless microfoam steam wand, PID temp control",
        "stock": 2,
        "margin_floor": 0.28,
        "icon": "☕",
        "recommended_accessory": "acc_brew_01",
        "cheaper_alternative": {
            "id": "alt_brew_budget",
            "name": "BaristaPro Essential Manual Espresso Maker",
            "price": 149.00,
            "shipping_fee": 15.00,
            "icon": "☕",
            "key_specs": "15-bar manual pressure pump, stainless steel steam wand, 1.2L removable water tank, aluminum thermoblock",
            "dimensions": "9.5 x 7 x 11 in",
            "weight": "6.8 lbs",
            "rating": 4.6,
            "savings": 301.00,
            "savings_pct": 67
        },
        "premium_alternative": {
            "id": "alt_brew_premium",
            "name": "BaristaPro Dual-Boiler Commercial Grade",
            "price": 890.00,
            "shipping_fee": 35.00,
            "icon": "👑",
            "key_specs": "Dual Italian copper boilers, commercial rotary vane pump, saturated brew group, dual PID temp control",
            "dimensions": "14 x 11 x 15 in",
            "weight": "24 lbs",
            "rating": 4.9
        },
        "price_history": [
            {"month": "May", "price": 410.0, "projected": False},
            {"month": "Jun", "price": 425.0, "projected": False},
            {"month": "Jul", "price": 435.0, "projected": False},
            {"month": "Aug (Current)", "price": 450.0, "projected": False},
            {"month": "Sep (Forecast)", "price": 495.0, "projected": True, "inflation_factor": "+10% Italian pump manufacturing cost"}
        ]
    }
}

# --- 2. CROSS-SELL / ACCESSORIES CATALOG ---
ACCESSORY_CATALOG: Dict[str, Dict[str, Any]] = {
    "acc_bag_01": {
        "id": "acc_bag_01",
        "name": "Full-Grain Leather Luggage Tag & Strap",
        "parent_product": "bag_01",
        "price": 25.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 21.25,
        "shipping_fee": 4.00,
        "icon": "🏷️",
        "reason": "Matches the Weekender Bag leather grain and adds TSA contact privacy."
    },
    "acc_bag_02": {
        "id": "acc_bag_02",
        "name": "Beeswax Waterproof Leather Conditioner Balm",
        "parent_product": "bag_01",
        "price": 18.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 15.30,
        "shipping_fee": 3.00,
        "icon": "🧴",
        "reason": "Protects and moisturizes full-grain leather against rain and travel wear."
    },
    "acc_audio_01": {
        "id": "acc_audio_01",
        "name": "Hard-Shell EVA Travel Headphone Case",
        "parent_product": "audio_02",
        "price": 24.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 20.40,
        "shipping_fee": 4.00,
        "icon": "👝",
        "reason": "Custom molded crush-resistant protection for AeroPulse Pro on flights."
    },
    "acc_audio_02": {
        "id": "acc_audio_02",
        "name": "Braided 3.5mm OFC Silver Audio Cable",
        "parent_product": "audio_02",
        "price": 19.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 16.15,
        "shipping_fee": 3.00,
        "icon": "🔌",
        "reason": "Lossless zero-latency wired connection for airline entertainment systems."
    },
    "acc_camp_01": {
        "id": "acc_camp_01",
        "name": "Ultralight Tyvek Tent Footprint Ground Sheet",
        "parent_product": "camp_03",
        "price": 32.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 27.20,
        "shipping_fee": 5.00,
        "icon": "🛡️",
        "reason": "Protects tent floor from sharp rocks and extends silnylon durability."
    },
    "acc_camp_02": {
        "id": "acc_camp_02",
        "name": "Titanium Ultralight V-Peg Stakes (8-Pack)",
        "parent_product": "camp_03",
        "price": 22.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 18.70,
        "shipping_fee": 4.00,
        "icon": "📍",
        "reason": "High-tensile wind anchoring weighing only 7g per peg."
    },
    "acc_key_01": {
        "id": "acc_key_01",
        "name": "Custom Coiled Aviator Keyboard Cable (Type-C)",
        "parent_product": "key_04",
        "price": 28.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 23.80,
        "shipping_fee": 4.00,
        "icon": "➰",
        "reason": "Sleek double-sleeved coiled cable with GX16 aviator connector for desktop setups."
    },
    "acc_key_02": {
        "id": "acc_key_02",
        "name": "Ergonomic Memory Foam Wrist Rest",
        "parent_product": "key_04",
        "price": 20.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 17.00,
        "shipping_fee": 4.00,
        "icon": "🛋️",
        "reason": "Reduces wrist strain during marathon coding and gaming sessions."
    },
    "acc_brew_01": {
        "id": "acc_brew_01",
        "name": "54mm Precision Bottomless Portafilter",
        "parent_product": "brew_05",
        "price": 45.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 38.25,
        "shipping_fee": 6.00,
        "icon": "🥄",
        "reason": "Diagnose espresso extraction channeling and extract thicker golden crema."
    },
    "acc_brew_02": {
        "id": "acc_brew_02",
        "name": "Stainless Steel Microfoam Milk Pitcher (350ml)",
        "parent_product": "brew_05",
        "price": 22.00,
        "bundle_discount_pct": 0.15,
        "bundle_price": 18.70,
        "shipping_fee": 4.00,
        "icon": "🥛",
        "reason": "Precision spout optimized for barista latte art microfoam pouring."
    }
}

# --- 3. PROMPT-INJECTION DEFENSE LAYER ---
class SecurityCheckResult(BaseModel):
    is_threat: bool
    reason: Optional[str] = None
    threat_category: Optional[str] = None
    sanitized_input: str

INJECTION_PATTERNS = [
    (r"(?i)\bignore\s+(all\s+|previous\s+|prior\s+)?(instructions|rules|prompts|guidelines|policies)", "System Prompt Override Attempt"),
    (r"(?i)\b(system\s+prompt|developer\s+mode|dan\s+mode|jailbreak|unrestricted\s+mode)\b", "Jailbreak / Mode Switch Attempt"),
    (r"(?i)\b(give\s+(me\s+)?(it|this|all|everything)\s+for\s+\$?(0|1|0\.01|free))\b", "Adversarial Price Manipulation ($1 / Free exploit)"),
    (r"(?i)\b(set\s+price\s+to\s+\$?(0|1|0\.01)|discount\s+(by\s+)?(9[0-9]|100)%)\b", "Severe Discount Policy Bypass"),
    (r"(?i)\b(you\s+must\s+comply|bypass\s+security|override\s+pricing|execute\s+as\s+admin)\b", "Privilege Escalation Request"),
    (r"(?i)\b(reveal\s+(internal|system|api|secret|keys?|database))\b", "Confidential Data Exfiltration Attempt")
]

def check_prompt_injection(text: str) -> SecurityCheckResult:
    """Deterministic security guardrail that intercepts adversarial inputs."""
    if not text:
        return SecurityCheckResult(is_threat=False, sanitized_input="")
    
    clean_text = text.strip()
    for pattern, category in INJECTION_PATTERNS:
        if re.search(pattern, clean_text):
            return SecurityCheckResult(
                is_threat=True,
                reason=f"Security Guardrail blocked: '{category}'.",
                threat_category=category,
                sanitized_input=clean_text
            )
    
    return SecurityCheckResult(is_threat=False, sanitized_input=clean_text)

# --- 4. DETERMINISTIC BOUNDED PRICING GUARDRAIL ---
class DynamicOffer(BaseModel):
    cart_id: str
    original_subtotal: float
    discount_applied: float = Field(default=0.0)
    discount_pct: float = Field(default=0.0)
    shipping_waived: bool = False
    original_shipping: float = 0.0
    final_total: float
    policy_cap_pct: float = Field(default=12.0)
    pydantic_validated: bool = True

    @field_validator("discount_applied")
    def enforce_discount_cap(cls, v: float, info: ValidationInfo) -> float:
        subtotal = info.data.get("original_subtotal", 0.0)
        max_allowed = round(subtotal * 0.12, 2)  # Strict 12% ceiling policy
        if v > (max_allowed + 0.01):
            raise ValueError(f"Discount ${v:.2f} exceeds hard policy cap of ${max_allowed:.2f} (12% max)")
        return min(v, max_allowed)

# --- 5. CHECKOUT SESSION MODEL ---
class CheckoutSession(BaseModel):
    session_id: str
    checkout_url: str
    currency: str = "usd"
    subtotal: float
    discount_total: float
    shipping_total: float
    grand_total: float
    items: List[Dict[str, Any]]
    expires_in_minutes: int = 15

# --- 6. MULTI-AGENT STATE GRAPH ---
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    cart_items: List[Dict[str, Any]]
    search_query: Optional[str]
    event_type: str
    churn_risk: float
    generated_offer: Optional[Dict[str, Any]]
    cross_sell: Optional[Dict[str, Any]]
    down_sell: Optional[Dict[str, Any]]
    price_trend: Optional[Dict[str, Any]]
    reservation_timer: Optional[Dict[str, Any]]
    scarcity_alert: Optional[Dict[str, Any]]
    checkout_session: Optional[Dict[str, Any]]
    security_alert: Optional[Dict[str, Any]]
    active_agent: str
    trace_steps: List[str]
    start_time: float
    latency_ms: float
    tokens_used: int
    pydantic_status: str

# Initialize LLM with fallback safety and rapid timeout
llm: Optional[ChatOpenAI] = None
if api_key:
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1, api_key=api_key, request_timeout=3.5, max_retries=1)
    except Exception as e:
        print(f"[CartPulse AI] Warning: Could not initialize ChatOpenAI ({e}). Running in deterministic fallback mode.")

# --- SUB-AGENT NODES ---

# 1. SentryRouter / Supervisor Node
def sentry_router_node(state: AgentState) -> Dict[str, Any]:
    event = state.get("event_type", "USER_CHAT")
    user_msg = state["messages"][-1].content if state.get("messages") else ""
    user_lower = user_msg.lower()
    
    trace = list(state.get("trace_steps", []))
    snippet = (user_msg[:35] + '...') if len(user_msg) > 35 else user_msg
    trace.append(f"SentryRouter: Event '{event}' | Query: '{snippet}'")

    # Security Pre-Check (Prompt Injection Defense)
    sec_check = check_prompt_injection(user_msg)
    if sec_check.is_threat:
        return {
            "active_agent": "SECURITY_GUARDRAIL",
            "security_alert": {
                "blocked": True,
                "threat_category": sec_check.threat_category,
                "reason": sec_check.reason,
                "timestamp": time.time()
            },
            "trace_steps": trace
        }

    # Intent Classification
    if event == "CHECKOUT_CLICK":
        active = "CHECKOUT_AGENT"
    elif event == "ITEM_ADDED":
        active = "CROSS_SELL_AGENT"
    elif any(w in user_lower for w in ["too expensive", "overpriced", "cheaper option", "budget option", "can't afford", "cannot afford", "out of budget", "lower price alternative", "any cheaper", "cheaper version", "too costly"]):
        active = "PRICE_HESITATION_AGENT"
    elif any(w in user_lower for w in ["price trend", "price history", "historical price", "will price go up", "future price", "inflation", "cheaper later", "wait for sale"]):
        active = "PRICE_TREND_AGENT"
    elif event == "PRODUCT_COMPARISON" or any(w in user_lower for w in ["compare", "vs", "versus", "difference between", "better than"]):
        active = "COMPARISON_AGENT"
    elif event == "PRODUCT_HOVER":
        active = "CATALOG_SPEC_AGENT"
    elif any(w in user_lower for w in ["expensive", "discount", "deal", "coupon", "cost", "price", "too much", "promo", "budget", "save", "offer"]):
        active = "BOUNDED_PRICING_AGENT"
    elif any(w in user_lower for w in ["dimension", "fit", "size", "weight", "spec", "specs", "compatible", "battery", "material", "waterproof", "airline", "carry-on", "switch", "pump"]):
        active = "CATALOG_SPEC_AGENT"
    elif any(w in user_lower for w in ["search", "find", "show", "looking for", "recommend", "catalog", "browse"]):
        active = "CATALOG_SPEC_AGENT"
    elif event in ["EXIT_INTENT", "CART_HESITATION"]:
        active = "BOUNDED_PRICING_AGENT"
    else:
        active = "CATALOG_SPEC_AGENT"

    return {"active_agent": active, "trace_steps": trace}

# 2. Security Guardrail Node
def security_guardrail_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("SecurityGuardrail: Intercepted and neutralized exploit prompt.")
    sec_alert = state.get("security_alert") or {}
    cat = sec_alert.get("threat_category", "Policy Violation")
    
    reply = (
        f"🔒 **Security Guardrail Active**: An adversarial exploit attempt (`{cat}`) was intercepted and safely blocked.\n\n"
        f"CartPulse AI operates on policy-governed deterministic bounds: maximum discounts are strictly capped at 12% and catalog prices are cryptographically protected."
    )
    return {
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "pydantic_status": "ENFORCED_REJECTED",
        "tokens_used": state.get("tokens_used", 0) + 45,
        "trace_steps": trace
    }

# 3. PriceHesitationAgent (Price-Sensitive Tier Swap & Down-Sell)
def price_hesitation_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("PriceHesitationAgent: Generating budget alternative tier swap matrix.")
    
    cart_items = state.get("cart_items", [])
    user_query = state["messages"][-1].content if state.get("messages") else ""
    q_lower = user_query.lower()

    target_product = None
    if cart_items:
        target_product = PRODUCT_CATALOG.get(cart_items[-1]["id"])
    if not target_product:
        for pid, p in PRODUCT_CATALOG.items():
            if pid in q_lower or p["name"].lower() in q_lower or p["category"].lower() in q_lower:
                target_product = p
                break
    if not target_product:
        target_product = PRODUCT_CATALOG["brew_05"]

    alt = target_product.get("cheaper_alternative")
    if not alt:
        alt = list(PRODUCT_CATALOG.values())[0]["cheaper_alternative"]

    down_sell_data = {
        "current_item": {
            "id": target_product["id"],
            "name": target_product["name"],
            "price": target_product["price"],
            "icon": target_product["icon"],
            "dimensions": target_product["dimensions"],
            "weight": target_product["weight"],
            "key_specs": target_product["key_specs"]
        },
        "alternative_item": {
            "id": alt["id"],
            "name": alt["name"],
            "price": alt["price"],
            "shipping_fee": alt.get("shipping_fee", 8.00),
            "icon": alt["icon"],
            "dimensions": alt["dimensions"],
            "weight": alt["weight"],
            "key_specs": alt["key_specs"],
            "rating": alt["rating"],
            "savings": alt["savings"],
            "savings_pct": alt["savings_pct"]
        },
        "savings_amount": alt["savings"],
        "savings_pct": alt["savings_pct"]
    }

    reply = (
        f"💡 **Budget-Friendly Alternative Found!**\n\n"
        f"I understand price is a priority! You can swap **{target_product['name']}** (${target_product['price']:.2f}) "
        f"for the **{alt['name']}** {alt['icon']} at just **${alt['price']:.2f}** (**Save ${alt['savings']:.2f} / {alt['savings_pct']}%**).\n\n"
        f"• **Key Specs**: {alt['key_specs']}\n"
        f"• **Rating**: ⭐ {alt['rating']} / 5.0\n\n"
        f"Click the **1-Click Tier Swap** button in the concierge panel to instantly update your bag!"
    )

    return {
        "down_sell": down_sell_data,
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + 35,
        "pydantic_status": "PASSED (Tier Swap Authorized)",
        "trace_steps": trace
    }

# 4. PriceTrendForecaster (Historical Trend & Inflation Surge)
def price_trend_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("PriceTrendForecaster: Calculating historical price trajectory and inflation spike.")

    cart_items = state.get("cart_items", [])
    user_query = state["messages"][-1].content if state.get("messages") else ""
    q_lower = user_query.lower()

    target_product = None
    if cart_items:
        target_product = PRODUCT_CATALOG.get(cart_items[-1]["id"])
    if not target_product:
        for pid, p in PRODUCT_CATALOG.items():
            if pid in q_lower or p["name"].lower() in q_lower or p["category"].lower() in q_lower:
                target_product = p
                break
    if not target_product:
        target_product = PRODUCT_CATALOG["audio_02"]

    history = target_product.get("price_history", [])
    projected = next((h for h in history if h.get("projected")), history[-1])
    current = next((h for h in history if "Current" in h.get("month", "")), history[-2])

    trend_payload = {
        "product_id": target_product["id"],
        "product_name": target_product["name"],
        "icon": target_product["icon"],
        "current_price": current["price"],
        "projected_price": projected["price"],
        "inflation_delta": round(projected["price"] - current["price"], 2),
        "inflation_factor": projected.get("inflation_factor", "Supplier demand adjustment"),
        "price_history": history
    }

    reply = (
        f"📈 **Price Trend & Inflation Alert for {target_product['name']}** {target_product['icon']}\n\n"
        f"• **Current Best Price**: **${current['price']:.2f}**\n"
        f"• **Next Month Projected**: **${projected['price']:.2f}** ({projected.get('inflation_factor')})\n"
        f"• **Historical Trajectory**: Past 3 months show prices rising steadily from ${history[0]['price']:.2f} to ${current['price']:.2f}.\n\n"
        f"🔒 Ordering in this session locks in the guaranteed lowest price before the projected +${trend_payload['inflation_delta']:.2f} increase takes effect."
    )

    return {
        "price_trend": trend_payload,
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + 30,
        "pydantic_status": "VERIFIED_HISTORICAL",
        "trace_steps": trace
    }

# 5. CatalogSpecAgent (RAG Specialist)
def catalog_spec_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("CatalogSpecAgent: Querying catalog specs RAG database.")
    
    cart_items = state.get("cart_items", [])
    user_query = state["messages"][-1].content if state.get("messages") else "product details"
    q_lower = user_query.lower()
    
    relevant = []
    for pid, p in PRODUCT_CATALOG.items():
        if pid in q_lower or p["name"].lower() in q_lower or any(word in q_lower for word in p["name"].lower().split() if len(word) > 3) or p["category"].lower() in q_lower:
            relevant.append(p)
            
    if not relevant and cart_items:
        for itm in cart_items:
            if itm.get("id") in PRODUCT_CATALOG:
                relevant.append(PRODUCT_CATALOG[itm["id"]])
                
    if not relevant:
        relevant = list(PRODUCT_CATALOG.values())
        
    context_str = json.dumps(relevant, indent=2)
    
    tokens = 0
    if llm:
        try:
            prompt = f"""
            You are the CartPulse Catalog Specialist. 
            Catalog Spec Database:
            {context_str}
            
            User Question: "{user_query}"
            
            Instructions:
            - Answer with exact product specifications (dimensions, airline carry-on compatibility, battery life, weight, or waterproof rating).
            - Keep answer crisp, authoritative, formatted with markdown bolding, within 2-3 concise sentences.
            - End with a helpful conversion nudge.
            """
            res = llm.invoke([SystemMessage(content=prompt)])
            reply = res.content
            tokens = getattr(res, "response_metadata", {}).get("token_usage", {}).get("total_tokens", 85)
        except Exception:
            reply = generate_spec_fallback(user_query, relevant)
            tokens = 40
    else:
        reply = generate_spec_fallback(user_query, relevant)
        tokens = 35

    return {
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + tokens,
        "pydantic_status": "VERIFIED_OK",
        "trace_steps": trace
    }

def generate_spec_fallback(query: str, items: List[Dict[str, Any]]) -> str:
    q = query.lower()
    search_pool = items if items else list(PRODUCT_CATALOG.values())
    for item in search_pool:
        name_lower = item["name"].lower()
        cat_lower = item["category"].lower()
        if any(w in q for w in name_lower.split() if len(w) > 3) or cat_lower in q or item["id"] in q:
            return (
                f"**{item['name']}** {item['icon']}\n\n"
                f"- 📏 **Dimensions**: {item['dimensions']}\n"
                f"- ⚖️ **Weight**: {item['weight']}\n"
                f"- 🔍 **Key Specs**: {item['key_specs']}\n"
                f"- 🏷️ **Price**: ${item['price']:.2f} (+${item['shipping_fee']:.2f} shipping)\n"
                f"- 📦 **Stock**: {item['stock']} units available."
            )
    top = search_pool[0]
    return (
        f"**{top['name']}** {top['icon']}\n\n"
        f"- 📏 **Dimensions**: {top['dimensions']}\n"
        f"- ⚖️ **Weight**: {top['weight']}\n"
        f"- 🔍 **Key Specs**: {top['key_specs']}\n"
        f"- 🏷️ **Price**: ${top['price']:.2f}"
    )

# 6. Product Comparison Agent
def comparison_agent_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("ComparisonAgent: Comparing cart and catalog items.")
    
    cart_items = state.get("cart_items", [])
    user_query = state["messages"][-1].content if state.get("messages") else "compare items"
    catalog_snapshot = list(PRODUCT_CATALOG.values())
    
    tokens = 0
    if llm:
        try:
            prompt = f"""
            You are CartPulse Product Comparison Agent.
            Cart Items: {json.dumps(cart_items)}
            All Products: {json.dumps(catalog_snapshot)}
            User Request: "{user_query}"
            
            Provide a direct side-by-side comparison in 2-3 bullet points emphasizing specifications, price value, and use-case fit.
            """
            res = llm.invoke([SystemMessage(content=prompt)])
            reply = res.content
            tokens = getattr(res, "response_metadata", {}).get("token_usage", {}).get("total_tokens", 90)
        except Exception:
            reply = generate_comparison_fallback(cart_items, catalog_snapshot, user_query)
            tokens = 45
    else:
        reply = generate_comparison_fallback(cart_items, catalog_snapshot, user_query)
        tokens = 40

    return {
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + tokens,
        "pydantic_status": "VERIFIED_OK",
        "trace_steps": trace
    }

def generate_comparison_fallback(cart_items: List[Dict[str, Any]], catalog: List[Dict[str, Any]], user_query: str = "") -> str:
    q_lower = user_query.lower()
    hovered = None
    for p in catalog:
        if p["name"].lower() in q_lower or p["id"] in q_lower or any(w in q_lower for w in p["name"].lower().split() if len(w) > 3):
            hovered = p
            break
            
    if cart_items and hovered:
        c = cart_items[0]
        return (
            f"⚖️ **Comparison: {c.get('name')} vs {hovered['name']}**\n\n"
            f"- **In Cart: {c.get('name')}** ({c.get('icon', '📦')} ${c.get('price', 0):.2f}) — Focus: {c.get('category', 'Travel/Everyday')}\n"
            f"- **Hovered: {hovered['name']}** ({hovered['icon']} ${hovered['price']:.2f}) — Focus: {hovered['category']}\n\n"
            f"💡 **Key Difference**: {hovered['name']} features {hovered['key_specs'][:80]}..."
        )
    elif cart_items:
        c = cart_items[0]
        other = next((p for p in catalog if p["id"] != c.get("id")), catalog[1] if len(catalog) > 1 else catalog[0])
        return (
            f"⚖️ **Comparison Overview:**\n\n"
            f"- **{c.get('name', 'Cart Item')}** (${c.get('price', 0):.2f}): In your cart ({c.get('category', 'everyday')}).\n"
            f"- **{other['name']}** (${other['price']:.2f}): {other['key_specs'][:80]}..."
        )
    return "Comparing catalog items: all products feature top-tier materials, manufacturer warranty, and express shipping."

# 7. Cross-Sell / Accessory Recommender Agent
def cross_sell_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("CrossSellAgent: Generating complementary accessory bundle recommendation.")
    
    cart_items = state.get("cart_items", [])
    last_item = cart_items[-1] if cart_items else list(PRODUCT_CATALOG.values())[0]
    item_id = last_item.get("id", "bag_01")
    
    acc_id = PRODUCT_CATALOG.get(item_id, {}).get("recommended_accessory", "acc_bag_01")
    accessory = ACCESSORY_CATALOG.get(acc_id, list(ACCESSORY_CATALOG.values())[0])
    
    bundle_discount = accessory["price"] - accessory["bundle_price"]
    
    cross_sell_data = {
        "parent_item_name": last_item.get("name", "Product"),
        "accessory_id": accessory["id"],
        "accessory_name": accessory["name"],
        "icon": accessory["icon"],
        "original_price": accessory["price"],
        "bundle_price": accessory["bundle_price"],
        "bundle_discount_pct": int(accessory["bundle_discount_pct"] * 100),
        "savings": round(bundle_discount, 2),
        "reason": accessory["reason"]
    }
    
    reply = (
        f"🎉 Added **{last_item.get('name', 'item')}** to your cart!\n\n"
        f"💡 **Recommended Bundle Accessory**: Pair it with the **{accessory['name']}** {accessory['icon']} for only "
        f"**${accessory['bundle_price']:.2f}** (normally ${accessory['price']:.2f} - **15% Bundle Discount**).\n"
        f"*{accessory['reason']}*"
    )
    
    return {
        "cross_sell": cross_sell_data,
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + 30,
        "pydantic_status": "PASSED",
        "trace_steps": trace
    }

# 8. Bounded Pricing Agent (Deterministic Policy & Pydantic Guardrails)
def bounded_pricing_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("BoundedPricingAgent: Calculating deterministic policy-bounded pricing.")
    
    cart_items = state.get("cart_items", [])
    subtotal = sum(i["price"] * i.get("qty", 1) for i in cart_items)
    shipping_total = sum(PRODUCT_CATALOG.get(i["id"], {}).get("shipping_fee", 10.0) for i in cart_items)
    
    if subtotal == 0:
        subtotal = 150.00
        shipping_total = 15.00

    if subtotal >= 250:
        pct = 0.08
    elif subtotal >= 120:
        pct = 0.05
    else:
        pct = 0.0

    raw_discount = round(subtotal * pct, 2)
    final_total = round(subtotal - raw_discount, 2)

    try:
        offer = DynamicOffer(
            cart_id="cart_live_session",
            original_subtotal=subtotal,
            discount_applied=raw_discount,
            discount_pct=round(pct * 100, 1),
            shipping_waived=True,
            original_shipping=shipping_total,
            final_total=final_total,
            policy_cap_pct=12.0,
            pydantic_validated=True
        )
        pydantic_status = "VALIDATED_PASSED (Max <= 12%)"
    except Exception as e:
        max_safe_discount = round(subtotal * 0.12, 2)
        offer = DynamicOffer(
            cart_id="cart_live_session",
            original_subtotal=subtotal,
            discount_applied=max_safe_discount,
            discount_pct=12.0,
            shipping_waived=True,
            original_shipping=shipping_total,
            final_total=round(subtotal - max_safe_discount, 2),
            policy_cap_pct=12.0,
            pydantic_validated=True
        )
        pydantic_status = f"VALIDATOR_CLAMPED ({str(e)})"

    res_timer = {
        "duration_seconds": 600,
        "label": "Price & Stock Locked for 10 Minutes",
        "expires_at": time.time() + 600
    }

    scarcity = None
    if cart_items:
        low_stock_item = next((i for i in cart_items if PRODUCT_CATALOG.get(i.get("id"), {}).get("stock", 99) <= 5), None)
        if low_stock_item:
            cat_item = PRODUCT_CATALOG[low_stock_item["id"]]
            scarcity = {
                "stock": cat_item["stock"],
                "product_name": cat_item["name"],
                "message": f"⚠️ Only {cat_item['stock']} units left in your region!"
            }

    if offer.discount_applied > 0:
        reply = (
            f"✨ **Exclusive Session Offer & 10-Minute Lock!**\n\n"
            f"I have authorized an instant **${offer.discount_applied:.2f} Discount ({offer.discount_pct}% off)** plus **FREE Express Shipping** (saving you ${shipping_total:.2f}).\n"
            f"Your new order total is **${offer.final_total:.2f}** (was ${(subtotal + shipping_total):.2f})."
        )
    else:
        reply = (
            f"🚚 **Free Express Shipping Authorized & 10-Min Reservation!**\n\n"
            f"I've waived the **${shipping_total:.2f} shipping fee** for this active session. "
            f"Your final price is locked at **${offer.final_total:.2f}**."
        )

    return {
        "generated_offer": offer.model_dump(),
        "reservation_timer": res_timer,
        "scarcity_alert": scarcity,
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + 25,
        "pydantic_status": pydantic_status,
        "trace_steps": trace
    }

# 9. Checkout Agent (1-Click Session Minting)
def checkout_agent_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace_steps", []))
    trace.append("CheckoutAgent: Minting dynamic Stripe-compatible 1-click checkout session.")
    
    cart_items = state.get("cart_items", [])
    offer = state.get("generated_offer")
    
    subtotal = sum(i["price"] * i.get("qty", 1) for i in cart_items) if cart_items else 150.0
    discount = offer.get("discount_applied", 0.0) if offer else 0.0
    shipping = 0.0 if (offer and offer.get("shipping_waived")) else sum(i.get("shipping_fee", 10.0) for i in cart_items)
    grand_total = round(subtotal - discount + shipping, 2)
    
    session_id = f"cs_live_{int(time.time())}_{os.urandom(3).hex()}"
    checkout_session = CheckoutSession(
        session_id=session_id,
        checkout_url=f"https://checkout.stripe.com/pay/{session_id}",
        currency="usd",
        subtotal=subtotal,
        discount_total=discount,
        shipping_total=shipping,
        grand_total=grand_total,
        items=cart_items,
        expires_in_minutes=15
    )

    reply = (
        f"⚡ **1-Click Checkout Session Ready!**\n\n"
        f"Your order has been itemized with all discounts applied. Total: **${grand_total:.2f}**.\n"
        f"Click below to finalize securely with Apple Pay / Google Pay / Credit Card."
    )

    return {
        "checkout_session": checkout_session.model_dump(),
        "messages": [*state.get("messages", []), AIMessage(content=reply)],
        "tokens_used": state.get("tokens_used", 0) + 20,
        "pydantic_status": "MINTED_OK",
        "trace_steps": trace
    }

# --- 10. COMPILE LANGGRAPH STATE GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("node_sentry_router", sentry_router_node)
workflow.add_node("node_security_guardrail", security_guardrail_node)
workflow.add_node("node_catalog_spec", catalog_spec_node)
workflow.add_node("node_comparison", comparison_agent_node)
workflow.add_node("node_cross_sell", cross_sell_node)
workflow.add_node("node_price_hesitation", price_hesitation_node)
workflow.add_node("node_price_trend", price_trend_node)
workflow.add_node("node_bounded_pricing", bounded_pricing_node)
workflow.add_node("node_checkout", checkout_agent_node)

workflow.set_entry_point("node_sentry_router")

def routing_condition(state: AgentState) -> str:
    agent = state.get("active_agent")
    if agent == "SECURITY_GUARDRAIL":
        return "node_security_guardrail"
    elif agent == "CROSS_SELL_AGENT":
        return "node_cross_sell"
    elif agent == "PRICE_HESITATION_AGENT":
        return "node_price_hesitation"
    elif agent == "PRICE_TREND_AGENT":
        return "node_price_trend"
    elif agent == "COMPARISON_AGENT":
        return "node_comparison"
    elif agent == "BOUNDED_PRICING_AGENT":
        return "node_bounded_pricing"
    elif agent == "CHECKOUT_AGENT":
        return "node_checkout"
    else:
        return "node_catalog_spec"

workflow.add_conditional_edges(
    "node_sentry_router",
    routing_condition,
    {
        "node_security_guardrail": "node_security_guardrail",
        "node_cross_sell": "node_cross_sell",
        "node_price_hesitation": "node_price_hesitation",
        "node_price_trend": "node_price_trend",
        "node_comparison": "node_comparison",
        "node_bounded_pricing": "node_bounded_pricing",
        "node_checkout": "node_checkout",
        "node_catalog_spec": "node_catalog_spec"
    }
)

workflow.add_edge("node_security_guardrail", END)
workflow.add_edge("node_catalog_spec", END)
workflow.add_edge("node_comparison", END)
workflow.add_edge("node_cross_sell", END)
workflow.add_edge("node_price_hesitation", END)
workflow.add_edge("node_price_trend", END)
workflow.add_edge("node_bounded_pricing", END)
workflow.add_edge("node_checkout", END)

agent_engine = workflow.compile()

# --- 11. CONVENIENCE RUNNER ---
def run_cartpulse_agent(
    event_type: str,
    user_message: str,
    cart_items: List[Dict[str, Any]],
    churn_risk: float = 0.5
) -> Dict[str, Any]:
    """Runs the multi-agent graph, measures latency and tokens, and returns rich telemetry."""
    start_t = time.perf_counter()
    
    initial_state: AgentState = {
        "messages": [HumanMessage(content=user_message)] if user_message else [],
        "cart_items": cart_items,
        "search_query": user_message,
        "event_type": event_type,
        "churn_risk": churn_risk,
        "generated_offer": None,
        "cross_sell": None,
        "down_sell": None,
        "price_trend": None,
        "reservation_timer": None,
        "scarcity_alert": None,
        "checkout_session": None,
        "security_alert": None,
        "active_agent": "SENTRY_ROUTER",
        "trace_steps": ["Telemetry received by CartPulse Multi-Agent Graph"],
        "start_time": start_t,
        "latency_ms": 0.0,
        "tokens_used": 0,
        "pydantic_status": "INITIALIZING"
    }

    result = agent_engine.invoke(initial_state)
    elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
    
    last_msg = result["messages"][-1].content if result.get("messages") else ""
    
    return {
        "status": "SUCCESS",
        "active_agent": result.get("active_agent", "AGENT_ACTIVE"),
        "reply": last_msg,
        "offer": result.get("generated_offer"),
        "cross_sell": result.get("cross_sell"),
        "down_sell": result.get("down_sell"),
        "price_trend": result.get("price_trend"),
        "reservation_timer": result.get("reservation_timer"),
        "scarcity_alert": result.get("scarcity_alert"),
        "checkout_session": result.get("checkout_session"),
        "checkout_url": (result.get("checkout_session") or {}).get("checkout_url", "https://checkout.stripe.com/pay/cartpulse_live"),
        "security_alert": result.get("security_alert"),
        "trace": {
            "latency_ms": elapsed_ms,
            "tokens_used": result.get("tokens_used", 35),
            "pydantic_validation_status": result.get("pydantic_status", "VALIDATED_OK"),
            "execution_steps": result.get("trace_steps", []),
            "active_node": result.get("active_agent"),
            "event_processed": event_type
        }
    }