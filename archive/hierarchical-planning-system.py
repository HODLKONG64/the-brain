"""
hierarchical-planning-system.py - Hierarchical Planning System for GK BRAIN
Plans narrative at immediate, daily, weekly and monthly timescales.
"""
import datetime, json, os
BASE_DIR = os.path.dirname(__file__)
PLAN_FILE = os.path.join(BASE_DIR, "narrative-plan.json")
BLOCK_GOALS = {"morning":"Begin with grounded presence — the activity, the place, the moment.","afternoon":"Develop the narrative thread started earlier. Deepen context.","evening":"Transition and reflect. Bridge activity to meaning.","night":"Full immersion. The peak experience or the quiet aftermath."}
WEEKLY_THEMES = ["Establishing presence","Building momentum","Facing complications","Finding breakthrough","Consolidating gains","Reflecting and planning","Rest and integration"]
MONTHLY_NARRATIVES = {1:"Winter reflection — craft, patience, the long view.",2:"Pre-season building — preparation, anticipation.",3:"Awakening — first signs of the active year ahead.",4:"Season opens — full engagement begins.",5:"Peak activity — everything firing simultaneously.",6:"Midsummer intensity — deepest immersion.",7:"Abundance — harvest the season's richness.",8:"Late season push — big moments approaching.",9:"Autumn depth — serious work, serious results.",10:"Peak performance — the year's biggest moments.",11:"Drawing in — consolidation and reflection.",12:"Year-end — maximum significance, every action counts."}

def get_narrative_plan(rule_ctx, lore_history=""):
    """Return multi-timescale narrative plan dict."""
    try:
        now = datetime.datetime.utcnow()
        block = rule_ctx.get("block","afternoon")
        week_num = now.isocalendar()[1] % 7
        plan = {"immediate_goal":BLOCK_GOALS.get(block,BLOCK_GOALS["afternoon"]),"daily_arc":f"Day {now.weekday()+1}/7 — {'fresh start, set intentions' if now.weekday()==0 else 'build on yesterday' if now.weekday()<4 else 'week climax approaching' if now.weekday()==4 else 'weekend energy shift'}","weekly_theme":WEEKLY_THEMES[week_num],"monthly_narrative":MONTHLY_NARRATIVES.get(now.month,"Continue the journey.")}
        return plan
    except Exception as e:
        print(f"[hierarchical-planning] {e}"); return {"immediate_goal":"Generate authentic lore.","daily_arc":"","weekly_theme":"","monthly_narrative":""}
