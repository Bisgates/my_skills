#!/usr/bin/env python3
"""distill_v2 headless QA. Renders the built single-file article in Chrome and
fails (exit 1) on any of:
  - external network request (not self-contained)
  - JS console / page error
  - KaTeX parse failure or DOUBLED math (shadow root missing KaTeX CSS)
  - a canvas far taller than its drawn content (>80px empty below the ink)
  - content drawn outside the canvas (clipped)
  - a slider/drag handler that blocks the main thread (>250ms synchronously) -> freeze

Usage: python3 bin/qa.py /abs/path/to/article.html
Requires: playwright (python) + Chrome/Chromium.
"""
import sys, json
from playwright.sync_api import sync_playwright


def qa(path):
    ext, errs = [], []
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 900})

        def route(r):
            u = r.request.url
            if not (u.startswith("file:") or u.startswith("data:")):
                ext.append(u); r.abort()
            else:
                r.continue_()

        ctx.route("**/*", route)
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.goto("file://" + path, wait_until="load")
        pg.wait_for_timeout(1800)

        res = pg.evaluate(r"""()=>{
          document.querySelectorAll('input[type=range]').forEach(s=>{
            s.value=s.max; s.dispatchEvent(new Event('input',{bubbles:true}));
          });
          function deep(sel){let n=0;const w=r=>{try{n+=r.querySelectorAll(sel).length;}catch(e){}
            r.querySelectorAll('*').forEach(el=>{if(el.shadowRoot)w(el.shadowRoot);});};w(document);return n;}
          let mathDoubled=0, mathChecked=0;
          document.querySelectorAll('d-math').forEach(dm=>{
            if(!dm.shadowRoot) return; mathChecked++;
            const styleLen=(dm.shadowRoot.querySelector('style')||{textContent:''}).textContent.length;
            const mml=dm.shadowRoot.querySelector('.katex-mathml');
            let vis=false; if(mml){const c=getComputedStyle(mml); vis=(c.position!=='absolute'&&c.clip==='auto');}
            if(styleLen<50 || (mml&&vis)) mathDoubled++;
          });
          // per-canvas geometry: ink bounding box vs allocated size
          const cv=[];
          document.querySelectorAll('canvas').forEach(c=>{
            const r=c.getBoundingClientRect(); let ink=null;
            try{const x=c.getContext('2d'),w=c.width,h=c.height,d=x.getImageData(0,0,w,h).data;
              let mnx=w,mny=h,mxx=0,mxy=0,any=false;
              for(let y=0;y<h;y+=2)for(let X=0;X<w;X+=2){const i=(y*w+X)*4;
                if(d[i+3]>10 && d[i]+d[i+1]+d[i+2]<740){any=true;if(X<mnx)mnx=X;if(X>mxx)mxx=X;if(y<mny)mny=y;if(y>mxy)mxy=y;}}
              const dpr=c.width/Math.max(1,r.width);
              if(any) ink={x:Math.round(mnx/dpr),y:Math.round(mny/dpr),w:Math.round((mxx-mnx)/dpr),h:Math.round((mxy-mny)/dpr)};
            }catch(e){}
            cv.push({id:c.id||'(noid)', cssW:Math.round(r.width), cssH:Math.round(r.height), ink});
          });
          return {
            dmath: document.querySelectorAll('d-math').length, katexRendered: deep('.katex'),
            rawDollarLeft: (document.body.innerText.match(/\$\$/g)||[]).length,
            title_h1: document.querySelectorAll('d-title h1').length,
            mathChecked, mathDoubled, canvases: cv,
          };
        }""")

        # freeze stress: time the synchronous cost of one input event per slider
        freeze = pg.evaluate(r"""()=>{
          let worst=0, who='';
          document.querySelectorAll('input[type=range]').forEach(s=>{
            const t0=performance.now();
            s.value = s.value; s.dispatchEvent(new Event('input',{bubbles:true}));
            const dt=performance.now()-t0; if(dt>worst){worst=dt; who=s.id||'(slider)';}
          });
          // synthetic drag on each canvas: a burst of moves (catches per-move heavy recompute)
          document.querySelectorAll('canvas').forEach(c=>{
            const r=c.getBoundingClientRect();
            const t0=performance.now();
            c.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:r.left+15,clientY:r.top+15,pointerId:1}));
            for(let k=0;k<12;k++){
              c.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:r.left+15+k*8,clientY:r.top+15+(k%3)*5,pointerId:1}));
            }
            c.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,clientX:r.left+110,clientY:r.top+30,pointerId:1}));
            const dt=performance.now()-t0; if(dt>worst){worst=dt; who=(c.id||'(canvas)')+':drag12';}
          });
          return {worstMs:Math.round(worst), who};
        }""")
        b.close()

    c = res
    fails = []
    if errs: fails.append(f"{len(errs)} console/page errors: {errs[:3]}")
    if ext: fails.append(f"{len(ext)} external requests: {ext[:3]}")
    if c["dmath"] and c["katexRendered"] < c["dmath"]:
        fails.append(f"math {c['katexRendered']}/{c['dmath']} rendered")
    if c.get("mathDoubled"):
        fails.append(f"DOUBLED math {c['mathDoubled']}/{c['mathChecked']}")
    if c["rawDollarLeft"]: fails.append(f"{c['rawDollarLeft']} raw $$ left")
    tall, clipped = [], []
    for cv in c["canvases"]:
        ink = cv["ink"]
        if not isinstance(ink, dict):
            continue
        bottom = ink["y"] + ink["h"]
        right = ink["x"] + ink["w"]
        if cv["cssH"] - bottom > 80:
            tall.append(f"{cv['id']}(+{cv['cssH']-bottom}px)")
        if bottom > cv["cssH"] + 6 or right > cv["cssW"] + 6:
            clipped.append(f"{cv['id']}(ink {right}x{bottom} > {cv['cssW']}x{cv['cssH']})")
    if tall: fails.append(f"TOO TALL (empty below ink): {tall}")
    if clipped: fails.append(f"CLIPPED (ink out of bounds): {clipped}")
    if freeze["worstMs"] > 250:
        fails.append(f"FREEZE risk: {freeze['who']} blocked {freeze['worstMs']}ms on one event")
    report = {"PASS": not fails, "fails": fails,
              "freeze_worst": freeze, "external": ext[:5], "console": errs[:5],
              "math": f"{c['katexRendered']}/{c['dmath']} (doubled {c.get('mathDoubled')})",
              "canvases": c["canvases"]}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(qa(sys.argv[1]))
