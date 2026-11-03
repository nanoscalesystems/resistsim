"""Build an offline evidence viewer. Does not run or calibrate the simulator."""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/experiments'
FILES = ('lu2025_fluorine_free_iline.json','liu2025_nonpfas_euv_gen2.json',
         'liu2026_265nm_e0.json','liu2026_solution_kinetics.json')


def load_datasets():
    result = {}
    for name in FILES:
        path = DATA/name
        if not path.exists():
            raise FileNotFoundError(f'Missing {path}; apply Steps 1 and 2 first.')
        result[name] = json.loads(path.read_text())
    return result


def esc(value):
    return html.escape(str(value))


def table(rows, columns):
    header = ''.join(f'<th scope="col">{esc(label)}</th>' for _,label in columns)
    body = ''.join('<tr>'+''.join('<td>'+esc('Not reported' if row.get(key) is None else row[key])+'</td>' for key,_ in columns)+'</tr>' for row in rows)
    return '<div class="scroll"><table><thead><tr>'+header+'</tr></thead><tbody>'+body+'</tbody></table></div>'


def provenance(data):
    return '<details><summary>Source data, conditions and limitations</summary><pre>'+esc(json.dumps(data,indent=2))+'</pre></details>'


def render(datasets):
    il, euv, clearing, kinetics = [datasets[n] for n in FILES]
    iltable = table(il['observations'], [('film_thickness_um','Film (µm)'),('pattern','Pattern'),('nominal_cd_um','Nominal CD (µm)'),('bottom_cd_um','Bottom CD (µm)'),('profile_delta_cd_pct','Profile ΔCD (%)'),('exposure_mj_cm2','Patterning dose (mJ/cm²)')])
    eut = table(euv['observations'],[('formulation','Formulation'),('pitch_nm','Pitch (nm)'),('dose_to_size_mj_cm2','Dose to size (mJ/cm²)'),('exposure_latitude_pct','EL (%)'),('dof_nm','DOF (nm)'),('biased_lwr_nm','Biased LWR (nm)'),('unbiased_lwr_nm','Unbiased LWR (nm)'),('unbiased_ler_nm','Unbiased LER (nm)')])
    ct = table(clearing['observations'],[('resist_registry_key','Resist'),('pag','PAG'),('peb_temperature_c','PEB (°C)'),('e0_mj_cm2','E₀ (mJ/cm²)'),('observation_type','Observation type')])
    kt = table(kinetics['monomers'], [('id','Monomer'),('published_ea_kcal_mol','Eₐ (kcal/mol)'),('published_ea_standard_error','Published fit SE (kcal/mol)'),('adopted_half_life_s','Half-life at 90°C / 1 M acid (s)')])
    content = f'''<section id="patterning"><h2>Fluorine-free patterning</h2><p>AZ FZero 3000 · i-line · NA 0.16 · thick-film packaging. Author-reported fluorine-free formulation.</p><p class="note">Profile ΔCD compares different heights in the resist. It is not mask-to-print bias. These exposures are not clearing doses.</p>{iltable}<p><a href="https://doi.org/10.1117/12.3050807">Lu et al., SPIE 2025</a> · Tables 1–3. The 100 µm film / nominal 10 µm hole has poor profile ΔCD; its inclusion is not a successful-resolution claim.</p>{provenance(il)}</section>
<section id="chemistry" hidden><h2>Clearing dose and solution kinetics</h2><h3>265 nm open-frame film measurements</h3>{ct}<p class="note">Non-clearing entries have no numeric E₀. Their source lower bounds remain in the evidence. These are not EUV measurements.</p>{provenance(clearing)}<h3>Solution kinetics</h3>{kt}<p>Independent solution-phase evidence from Step 2. Its measured rates do not directly set film reaction rates. Expand the source record for all measurements and the preserved half-life discrepancy.</p>{provenance(kinetics)}<p>Run <code>python scripts/solution_kinetics.py</code> to reconstruct the Arrhenius summaries.</p></section>
<section id="euv" hidden><h2>EUV measurements</h2><p>Gen-2 paired formulations · 13.5 nm · 30 nm film on SiARC · PAB 110°C / 60 s · PEB 100°C / 60 s · 0.26 N TMAH / 30 s.</p><p class="note">Reported benchmarks, not calibrated simulator predictions. Dose to size ≠ dose to clear. Roughness definitions differ between pitches. Uncertainties and full process-window criteria are not supplied.</p>{eut}<p class="note">Source conflict: non-PFAS 28 nm-pitch uLER is 1.75 nm in Table 8, but 1.85 nm in the prose. Table value displayed provisionally; no author correction confirmed.</p><p><a href="https://doi.org/10.1117/12.3050881">Liu et al., SPIE 2025</a> · Tables 7–8. Proprietary composition and absolute loadings remain undisclosed.</p>{provenance(euv)}</section>'''
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Resistsim · Experimental evidence</title><style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#071014;color:#dce9ef}body{max-width:1200px;margin:auto;padding:24px}h1{font-size:clamp(1.8rem,5vw,3rem)}h2{color:#64ddeb}p{line-height:1.6}nav{display:flex;gap:10px;flex-wrap:wrap;margin:25px 0}button{font:inherit;color:inherit;background:#14262e;border:1px solid #44606c;padding:12px;cursor:pointer;border-radius:6px}button[aria-pressed=true]{background:#135d6a;border-color:#64ddeb}button:focus-visible{outline:3px solid white}.note{padding:14px;border-left:3px solid #64ddeb;background:#10232b}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{padding:12px;text-align:left;border-bottom:1px solid #29404b}th{background:#10232b}details{margin:20px 0;padding:15px;border:1px solid #29404b}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem}a{color:#64ddeb}code{overflow-wrap:anywhere}[hidden]{display:none}footer{margin-top:32px;color:#a8bdc7}
</style><header><p>NANOSCALE SYSTEMS / RESISTSIM</p><h1>Experimental evidence</h1><p>Explore measured patterning, clearing doses and reaction kinetics. Each dataset retains its formulation, processing conditions and limitations.</p></header><nav aria-label="Evidence views"><button aria-pressed="true" data-view="patterning">Fluorine-free patterning</button><button aria-pressed="false" data-view="chemistry">Clearing dose &amp; kinetics</button><button aria-pressed="false" data-view="euv">EUV measurements</button></nav><noscript><p>Enable JavaScript to switch views; source JSON remains available in the repository.</p></noscript>'''+content+'''<footer>Evidence viewer only. No simulation defaults changed. Missing measurements are not zero.</footer><script>document.querySelectorAll('button[data-view]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('section').forEach(s=>s.hidden=s.id!==b.dataset.view);document.querySelectorAll('button[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));}));</script></html>'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'evidence-preview.html')
    args=parser.parse_args()
    output=render(load_datasets())
    with args.output.open('x') as f:
        f.write(output)
    print('Created:',args.output)
    print('Open in a browser. Existing output files are never overwritten.')


if __name__=='__main__':
    main()
