#!/usr/bin/env python3
"""Supplementary Note "System-by-system summary": of the 34 benchmark problems (suppl_systems.tex).

The numbers (sizes, subsets, conditioning, e_fit, level, pattern, validation) are read from results/;
the description of each model and of the role of each selected parameter was written from the
reactions and rules of the SBML model in which the parameter appears (problems/<problem>/v1/model.xml
of the PEtab benchmark collection) and from the source publication, whose DOI or PubMed identifier is
taken from the overview table of the collection (stored in problem_sources.json).
"""
import json, re
import numpy as np

from common import efit_final, fmt_efit, HERE as SRC, OUT as HERE, RESULTS, load, load_validation

SEL, VAL, PAT = load("selection"), load_validation(), load("robustness")

# DOI (or PubMed id) of the source publication, from the overview table of the benchmark collection
DOI = {k: tuple(v) for k, v in json.loads((SRC / "problem_sources.json").read_text()).items()}

# models with a Lean proof (Supplementary Note "Verified benchmark models") and reason for the others
NOT_VERIFIED = {
    "Alkan_SciSignal2018": "the automatic checks of the domain and quasi-positivity conditions fail",
    "Beer_MolBioSystems2014": "the growth check fails",
    "Liu_IFACPapersOnLine2025": "the model has events that depend on the state",
    "Oliveira_NatCommun2021": "the model has events that depend on the parameters",
    "Perelson_Science1996": "the quasi-positivity check fails for two terms",
    "Schwen_PONE2014": "the quasi-positivity check fails for two terms",
    "Smith_BMCSystBiol2013": "the rate laws contain a non-differentiable maximum",
}

NOT_EVALUABLE = {
    "Bertozzi_PNAS2020": "both selected parameters belong only to the held-out condition, so they cannot be estimated from the training data",
    "Blasi_CellSystems2016": "the problem has a single condition and a single measurement time, so the data cannot be split",
}

# model (one sentence) and role of the selected parameters, written from the SBML reactions
TXT = {
    "Alkan_SciSignal2018": (
        "Cell-cycle progression, DNA double-strand-break damage and repair under chemotherapy (36 species).",
        r"\texttt{kt} is the cell-cycle transition rate, shared by the transitions G1$\to$S, S$\to$G2 and G2$\to$division; "
        r"\texttt{k\_rep\_nhej} is the rate of repair by non-homologous end joining, which returns damaged S and G2 cells to the cycle."),
    "Armistead_CellDeathDis2024": (
        "Ceramide and sphingolipid metabolism (4 species).",
        r"\texttt{k\_d} is the degradation rate of ceramide; \texttt{k00} is the basal rate of de novo production of sphinganine."),
    "Bachmann_MSB2011": (
        "JAK2/STAT5 signalling induced by erythropoietin (Epo) with negative feedback by CIS and SOCS3 (25 species).",
        r"\texttt{JAK2ActEpo} is the rate of Epo-induced activation of JAK2 at the receptor (EpoR:JAK2 $\to$ EpoR:pJAK2); "
        r"\texttt{CISRNADelay} is the transit rate through the chain of delay compartments of CIS mRNA, i.e.\ it sets the delay of the CIS feedback."),
    "Beer_MolBioSystems2014": (
        "Growth of bacterial cultures and production of the pigment indigoidine by engineered synthetase variants (4 species, 19 conditions).",
        None),
    "Bertozzi_PNAS2020": (
        "SIR model of the COVID-19 epidemic, fitted to two regions (3 species).",
        r"\texttt{R0\_NY} is the basic reproduction number in New York, which sets the infection rate; \texttt{I0\_NY} is the initial number of infected individuals in New York."),
    "Blasi_CellSystems2016": (
        "Acetylation of the four lysines of histone H4 (16 acetylation states).",
        r"\texttt{a\_basal} is the basal acetylation rate, from which most of the transition rates are derived by assignment rules; "
        r"\texttt{a\_k16\_k12k16} is the rate of acetylation of K12 in H4 already acetylated at K16."),
    "Boehm_JProteomeRes2014": (
        "Phosphorylation, dimerisation and nuclear import of STAT5A and STAT5B (8 species).",
        r"\texttt{k\_phos} is the rate of phosphorylation and dimerisation of STAT5 (the three reactions forming pApA, pApB and pBpB); "
        r"\texttt{k\_imp\_hetero} is the rate of nuclear import of the heterodimer pApB."),
    "Borghans_BiophysChem1997": (
        "Intracellular Ca$^{2+}$ oscillations by Ca$^{2+}$-induced Ca$^{2+}$ release (3 species).",
        r"\texttt{Kz} is the threshold constant of the release of Ca$^{2+}$ from the Ca$^{2+}$-sensitive pool into the cytosol; "
        r"\texttt{K\_par} is the constant of the removal of cytosolic Ca$^{2+}$."),
    "Brannmark_JBC2010": (
        "Insulin signalling in adipocytes: insulin receptor and IRS1 phosphorylation and internalisation (9 species).",
        r"\texttt{k1f} is the rate of dephosphorylation and recycling of the internalised phosphorylated receptor (IRiP $\to$ IRi); "
        r"\texttt{km2} is the rate of dephosphorylation of IRS1 (IRSiP $\to$ IRS)."),
    "Bruno_JExpBot2016": (
        "Enzymatic cleavage of carotenoids ($\\beta$-carotene, $\\beta$-cryptoxanthin, zeaxanthin) into apocarotenoids (7 species, 6 experiments).",
        r"\texttt{kb1} is the cleavage rate of $\beta$-carotene; the other four are initial amounts of the substrates in particular experiments: "
        r"$\beta$-carotene (\texttt{init\_bcar1}, \texttt{init\_bcar2}), zeaxanthin (\texttt{init\_zea\_1}) and $\beta$-cryptoxanthin (\texttt{init\_bcry\_1})."),
    "Chen_MSB2009": (
        "ErbB receptor network (ErbB1--4) with the MAPK and PI3K/AKT cascades (500 species).",
        r"\texttt{k106} is the binding rate of PIP2 to the receptor complexes that carry PI3K; "
        r"\texttt{k44} is the binding rate of MEK to phosphorylated Raf, the first step of MEK activation."),
    "Crauste_CellSystems2017": (
        "CD8 T-cell response to infection: naive, early and late effector and memory cells and pathogen (5 species).",
        None),
    "Elowitz_Nature2000": (
        "The repressilator, a synthetic oscillator of three mutually repressing genes with a GFP reporter (8 species).",
        r"\texttt{n\_Hill} is the Hill coefficient of transcriptional repression, shared by the four transcription reactions; "
        r"\texttt{tau\_mRNA} is the mRNA lifetime, which enters the degradation of the three mRNAs and the translation rates."),
    "Fiedler_BMCSystBiol2016": (
        "RAF/MEK/ERK cascade with ERK feedback, under different inhibitor treatments (6 species).",
        r"\texttt{tau2} is a time constant of the activation input of RAF; "
        r"\texttt{k6} is the rate of dephosphorylation of pERK, and it also enters the steady state from which every simulation starts."),
    "Fujita_SciSignal2010": (
        "EGF-dependent AKT signalling and S6 phosphorylation (9 species).",
        r"\texttt{init\_AKT} is the initial amount of AKT; \texttt{reaction\_6\_k1} is the rate of release of pAKT and pS6 from the pAKT:S6 complex, i.e.\ of S6 phosphorylation."),
    "Giordano_Nature2020": (
        "SIDARTHE model of the COVID-19 epidemic in Italy, with parameters that change at the dates of the containment measures (8 species).",
        r"\texttt{alpha\_4} and \texttt{alpha\_28} are the transmission coefficient $\alpha$ (infection by undetected asymptomatic individuals) after the changes of day 4 and day 28."),
    "Isensee_JCB2018": (
        "Activation of protein kinase A type II by cAMP in sensory neurons (25 species).",
        r"\texttt{kf\_RIIp\_C\_2\_\_RII\_C\_2} is the rate of dephosphorylation of the regulatory subunit within the holoenzyme (pRII$_2$:C$_2$ $\to$ RII$_2$:C$_2$); "
        r"\texttt{xi\_kf\_RII\_C\_2\_\_RII\_2} is the factor that scales the dissociation of the catalytic subunits from the phosphorylated holoenzyme."),
    "Lang_PLOSComputBiol2024": (
        "Mammalian cell cycle (E2F, RB, cyclins and CDK inhibitors) in the cytoplasm and nucleus (several hundred species).",
        r"\texttt{kDeE2f1} is the degradation rate of E2F1, shared by all the complexes that contain it; "
        r"\texttt{kDeCe} is the degradation rate of cyclin E in its complexes with the CDK inhibitors p21 and p27."),
    "Laske_PLOSComputBiol2019": (
        "Influenza A virus replication: nuclear import of viral ribonucleoproteins and viral RNA synthesis.",
        r"\texttt{k\_imp} is the rate of nuclear import of viral ribonucleoproteins (cytoplasm $\to$ nucleus); "
        r"\texttt{k\_syn\_R\_M} is the synthesis rate of viral mRNA, from which the rates of the eight mRNA segments are derived."),
    "Liu_IFACPapersOnLine2025": (
        "Virus--cell model: uninfected cells with logistic growth, five stages of infected cells and free virus (7 states, written as rate rules).",
        r"\texttt{kappa} is the carrying capacity of the logistic growth of the cells; \texttt{phi} is the rate of transition between successive stages of infection."),
    "Lucarelli_CellSystems2018": (
        "TGF-$\\beta$/SMAD signalling and the expression of its target genes (several dozen species).",
        r"\texttt{init\_Rec} is the amount of receptor; \texttt{S2tot}, \texttt{S3tot} and \texttt{S4tot} are the total amounts of SMAD2, SMAD3 and SMAD4; "
        r"\texttt{S\_phos} and \texttt{S\_dephosphos} are the rates of phosphorylation and dephosphorylation of SMAD2/3; "
        r"\texttt{k\_234} is the rate of formation of the ppSMAD2:ppSMAD3:SMAD4 complex; "
        r"\texttt{geneF\_turn}, \texttt{geneH\_turn} and \texttt{geneK\_turn} are the turnover rates of three target genes."),
    "Okuonghae_ChaosSolitonsFractals2020": (
        "Model of the COVID-19 epidemic in Lagos, Nigeria, with detected and undetected infected classes (9 species).",
        r"\texttt{transmission\_rate\_effective} is the effective transmission rate (force of infection, susceptible $\to$ exposed); "
        r"\texttt{gamma\_i} is the recovery rate of detected infected individuals."),
    "Oliveira_NatCommun2021": (
        "Model of the COVID-19 epidemic in Bahia, Brazil, with hospital and intensive-care compartments.",
        r"\texttt{beta\_0} is the transmission rate (susceptible $\to$ exposed); "
        r"\texttt{h\_hosp\_rate} is the fraction of symptomatic individuals who are hospitalised, which splits the outflow of symptomatic cases between recovery, hospital and ICU."),
    "Perelson_Science1996": (
        "HIV-1 dynamics in a patient treated with a protease inhibitor (infected cells, infectious and non-infectious virus).",
        r"\texttt{c} is the clearance rate of free virions; \texttt{delta} is the death rate of productively infected cells."),
    "Rahman_MBS2016": (
        "Transmission model with infected classes of different severity and a treated class.",
        r"\texttt{infected\_moderate\_transmission\_rate} is the transmission rate of moderately infected individuals, to which the rates of the other classes are tied by assignment rules (it sets the force of infection); "
        r"\texttt{infected\_normal\_worsen\_rate} is the rate of progression from normal to moderate infection."),
    "Raia_CancerResearch2011": (
        "IL-13 signalling through JAK/STAT6 with SOCS3 feedback in Hodgkin lymphoma cells (several dozen parameters, 4 conditions).",
        r"\texttt{SOCS3mRNA\_production} is the production rate of SOCS3 mRNA, which drives the negative feedback; "
        r"\texttt{init\_Rec\_i} is the initial amount of internalised receptor, which is recycled to the membrane."),
    "Raimundez_PCB2020": (
        "EGFR and MET signalling in two gastric cancer cell lines (MKN1 and HS746T) treated with EGF, HGF and cetuximab.",
        r"\texttt{kdeg\_membran\_\_MKN1} is the degradation rate of membrane receptors (EGFR, EGFR:EGF, EGFR:cetuximab) in MKN1 cells; "
        r"\texttt{ka\_MAPK\_\_MKN1} is the rate constant of MAPK (ERK) phosphorylation in MKN1 cells; its published value lies at the upper bound of the benchmark range ($10^3$)."),
    "SalazarCavazos_MBoC2020": (
        "Multisite phosphorylation of the epidermal growth factor receptor (EGFR).",
        r"\texttt{ratio\_kpkd\_Y1068\_\_FREE} and \texttt{ratio\_kpkd\_YN\_\_FREE} are the ratios of phosphorylation to dephosphorylation rate of tyrosine Y1068 and of the other tyrosines in receptors that are not bound to adaptor proteins."),
    "Schwen_PONE2014": (
        "Binding and uptake of insulin by hepatocytes through receptors of low and high affinity.",
        r"\texttt{ini\_R1} is the initial amount of low-affinity receptors, and \texttt{ini\_R2fold} the factor that gives the amount of high-affinity receptors from it; both set the binding and uptake of insulin."),
    "Smith_BMCSystBiol2013": (
        "Insulin signalling through IRS1, PI3K and serine phosphorylation of IRS1.",
        r"\texttt{k8} is the binding rate of PI3K to tyrosine-phosphorylated IRS1; "
        r"\texttt{kminus7b} is the rate of removal of the serine phosphorylation of IRS1 (reverse of the inhibitory serine phosphorylation)."),
    "Sneyd_PNAS2002": (
        "Gating of the IP$_3$ receptor Ca$^{2+}$ channel (open, shut and inactivated states).",
        r"\texttt{l2} and \texttt{l4} are rate constants of the Ca$^{2+}$-dependent transitions of the receptor from the rest state to the open and inactivated states."),
    "Weber_BMC2015": (
        "Feedback between protein kinase D (PKD), the ceramide transfer protein CERT and PI4KIII$\\beta$ at the Golgi.",
        r"\texttt{s12} is the constant production rate of PKD; \texttt{a21} is the first-order removal rate of PI4KIII$\beta$."),
    "Zhao_QuantBiol2020": (
        "Model of the COVID-19 epidemic in China with unquarantined and quarantined infected individuals, in two stages and three regions.",
        r"\texttt{R\_Stage\_I\_China} and \texttt{R\_Stage\_II\_Wuhan} are the reproduction numbers of stage~I in China and of stage~II in Wuhan, which set the infection rate; "
        r"\texttt{gamma\_1\_Stage\_I\_Hubei} is the quarantine rate of infected individuals in Hubei in stage~I."),
    "Zheng_PNAS2012": (
        "Methylation of histone H3 at lysines 27 and 36 (combinatorial methylation states).",
        r"\texttt{k01\_02} is the rate of methylation of K36 from mono- to dimethyl in histones without K27 methylation; "
        r"\texttt{k13\_12} is the rate of demethylation of K36 from tri- to dimethyl in histones with K27me1."),
}


def tex(s):
    return s.replace("_", r"\_")


def chi(x):
    if x < 0.01:
        return r"$<$0.01"
    if x < 100:
        return f"{x:.2f}"
    return f"{x:,.0f}"


def nivel(d):
    if not d.get("admisible"):
        return None
    if d["cos_med"] >= 0.9:
        return 3 if d["Rvar_%"] >= 89 else 2
    return 1


LEVEL = {1: r"level~1 ($e_{\mathrm{fit}}\le\tau_e$ only)",
         2: r"level~2 ($\cos\Delta\ge0.9$ as well)",
         3: r"level~3 ($\cos\Delta\ge0.9$ and $R_{\mathrm{var}}\ge0.89$)"}
PATTERN = {"A": "pattern~A: admissible at all perturbation sizes up to $\\pm$50\\%",
           "B": "pattern~B: admissible up to at least $\\pm$20\\% but not for larger changes",
           "C": "pattern~C: irregular, with an error that stays close to the threshold and crosses it at some sizes"}


def validation(s, d):
    v = VAL.get(s, {})
    if s in NOT_EVALUABLE:
        return f"External validation was not possible: {NOT_EVALUABLE[s]}."
    split = v["division"]
    if split.startswith("condiciones"):
        how = f"held-out experimental conditions ({int(v['n_test'])} test and {int(v['n_train'])} training measurements)"
    else:
        t = re.search(r"t ≥ ([\d.]+)", split).group(1)
        how = f"later time points ($t\\ge{float(t):g}$; {int(v['n_test'])} test and {int(v['n_train'])} training measurements)"
    r, f, t0 = v["A_chi2_test_red"], v.get("A_chi2_test_full"), v["A_chi2_test_theta0"]
    out = f"External validation on {how}: test $\\chi^2/n$ {chi(r)} for the reduced model"
    if f is None or not np.isfinite(f):
        out += f" (published $\\theta_0$: {chi(t0)}); the refit of the full model is still running."
        return out
    out += f", {chi(f)} for the full model refitted to the same data and {chi(t0)} for the published $\\theta_0$. "
    if max(r, f) < 0.01:
        out += "All fits reproduce the data almost exactly, so the comparison is not informative."
    elif abs(r - f) <= 0.002 * f:
        out += "The two refitted models predict equally well."
    elif r < f:
        ft = v.get("A_chi2_train_full")
        if f > 3 * r and ft is not None and ft < f / 3:
            out += (f"The reduced model, anchored at $\\theta_0$, predicts the test data better than the refitted "
                    f"full model, which fits the training data closely ($\\chi^2/n$ {chi(ft)}) but predicts the "
                    f"test data poorly, a sign of overfitting.")
        elif f > 3 * r:
            out += ("The reduced model, anchored at $\\theta_0$, predicts the test data much better than the "
                    "refitted full model.")
        else:
            out += ("The reduced model, anchored at $\\theta_0$, predicts the test data better than the refitted "
                    "full model.")
    else:
        out += "Here the refitted full model predicts the test data better than the reduced model."
    if t0 > 10:
        out += (" Even $\\theta_0$ has $\\chi^2/n\\gg1$, which indicates that the noise levels recorded in the benchmark "
                "do not match the scatter of the data.")
    return out


def paragraph(s):
    d = SEL[s]
    what, roles = TXT[s]
    S = d["S"]
    nc = len(d.get("calibracion", []))
    short = s.split("_")[0]
    L = [rf"\subsection*{{{tex(s)}}}", ""]
    kind, ref = DOI[s]
    src = (rf" Source: \href{{https://doi.org/{ref}}}{{\nolinkurl{{doi:{ref}}}}}." if kind == "doi"
           else rf" Source: \href{{https://pubmed.ncbi.nlm.nih.gov/{ref}/}}{{PubMed {ref}}}.")
    size = f"The full model has {d['p']} parameters" + (f", {nc} of which are measurement calibration parameters (scales, offsets or noise levels) that are always re-estimated" if nc else "") + "."
    head = f"{what}{src} {size}"
    if s == "Crauste_CellSystems2017":
        B = json.loads((RESULTS / "crauste_blowup.json").read_text())
        fails = [r for r in B["un_parametro_1%"] if not r["existe_en_[0,28]"]]
        tb = [r["t_final"] for r in fails]
        f5 = {t["fallos_escenarios_5%"] for t in B["tolerancias"]}
        f1 = {t["fallos_un_parametro_1%"] for t in B["tolerancias"]}
        assert len(f5) == 1 and len(f1) == 1                     # the same at every integrator tolerance
        nom = B["nominal"]
        L.append(head + r" \textbf{Not admissible.} The published parameters lie at the edge of a regime in which the solution grows without bound in finite time. "
                 rf"With the published parameters the effector populations reach a peak of ${nom['efectores_max'] / 10 ** int(np.floor(np.log10(nom['efectores_max']))):.1f}\times10^{{{int(np.floor(np.log10(nom['efectores_max'])))}}}$ cells on day {nom['t_max']:.1f} and then decline "
                 rf"({nom['efectores_t_final']:.0f} cells on day 28); after a change of only 1\% in a single parameter (for example, a decrease of the proliferation rate of early effectors $\rho_E$) "
                 rf"they keep growing and the solution breaks down between days {min(tb):.1f} and {max(tb):.1f}, well within the measured horizon of 28 days. "
                 rf"This happened for {len(fails)} of the 24 one-at-a-time perturbations of $\pm$1\% and for {f5.pop().split('/')[0]} of the 15 scenarios at $\pm$5\%, "
                 r"for every integrator tolerance tested (relative tolerances from $10^{-10}$ to $10^{-5}$), "
                 r"so the sensitivity matrix and the admissibility test are not defined and no local reduction method is applicable. "
                 r"Consistently, the existence of solutions could only be proved in Lean on a short horizon ($T\le1$, \sref{models}).")
        return L
    if s == "Lang_PLOSComputBiol2024" and not d.get("admisible"):
        nl = ", ".join(rf"\texttt{{{tex(x)}}}" for x in S[:-1]) + rf" and \texttt{{{tex(S[-1])}}}"
        L.append(head + rf" \textbf{{Not admissible.}} Ranking by finite-perturbation effects (stage~2), the selection stopped at {len(S)} parameters ({nl}), "
                 rf"because any further parameter violated the conditioning test ($\kappa={d['kappa']:.1f}$, VIF ${d['VIF']:.2f}$, just below the limit of 10). "
                 rf"Re-estimating these {len(S)} parameters gave a median first-order $e_{{\mathrm{{fit}}}}$ of {100*d['eajuste_med']:.0f}\%, above the threshold of 43.6\%. "
                 r"Admissible pairs nevertheless exist: on the same scenarios, the search with conditioning thresholds of 5 or 30 instead of 10 (Supplementary Note \emph{Random scenarios and large problems}, Supplementary Table~\ref{tab:settingsextra}) adds a different second parameter and finds \{\texttt{kDeE2f1}, \texttt{kSySkp2}\} ($e_{\mathrm{fit}}=13\%$) and \{\texttt{kDeE2f1}, \texttt{kSyCb1}\} ($e_{\mathrm{fit}}=16\%$). "
                 r"With the default threshold the second parameter is \texttt{kDeCe}, whose pair is not admissible, and the greedy search then grows until the conditioning limit without becoming admissible; the failure is therefore a limitation of the greedy search in this oscillating cell-cycle model (simulated to $t=136{,}472$), not evidence that no small subset exists. "
                 r"Our simulation of this model also differs from the reference simulation of the benchmark more than in any other problem (22\% of the measurements by more than one noise unit; Supplementary Note \emph{Verification of the simulator}), so this result should be read with that caveat.")
        return L
    if s == "Beer_MolBioSystems2014":
        L.append(head + rf" \textbf{{Not admissible.}} The selection stopped at {len(S)} parameters (synthesis, dimerisation and degradation rates of particular strains, growth rates $\beta$ of particular experiments and the initial amount of bacteria), "
                 rf"because any further parameter violated the conditioning test ($\kappa={d['kappa']:.1f}$, VIF ${d['VIF']:.3f}$, just below the limit of 10). "
                 rf"Re-estimating these {len(S)} parameters gave a median $e_{{\mathrm{{fit}}}}$ of {100*d['eajuste_med']:.0f}\%, above the threshold of 43.6\%; "
                 r"the outputs depend on many strain- and experiment-specific parameters, and no small subset can compensate for all of them. "
                 rf"The Lean verification of this model is only conditional, because {NOT_VERIFIED[s]}.")
        return L
    names = ", ".join(rf"\texttt{{{tex(x)}}}" for x in S[:-1]) + rf" and \texttt{{{tex(S[-1])}}}"
    st = "1, ranking by sensitivity energy" if d["etapa"] == "Stage 1" else "2, ranking by finite-perturbation effects"
    num = {2: "two", 3: "three", 5: "five", 10: "ten"}[len(S)]
    sel = f"The method selected {num} biological parameters, {names} (stage~{st})"
    pod = d.get("podados") or []
    if pod:
        pn = [rf"\texttt{{{tex(x)}}}" for x in pod]
        pn = pn[0] if len(pn) == 1 else ", ".join(pn[:-1]) + " and " + pn[-1]
        sel += f"; backward elimination had removed {pn} from the initial selection"
    sel += f"; the reduced problem has {100 * (1 - (len(S) + nc) / d['p']):.0f}\\% fewer free parameters than the full one. "
    lv, pt = nivel(d), PAT[s]["patron"]
    eff, nl = efit_final(s, d)
    efs = fmt_efit(eff) + (rf" (nonlinear re-estimation of the final subset; {100 * d['eajuste_med']:.1f}\% to first order during the selection)" if nl else "")
    met = (rf"For this subset $\kappa={d['kappa']:.1f}$ and VIF ${d['VIF']:.1f}$ (no collinearity), $R_{{\mathrm{{var}}}}={d['Rvar_%']:.0f}\%$, "
           rf"median $\cos\Delta={d['cos_med']:.2f}$ and median $e_{{\mathrm{{fit}}}}={efs}\%$ at $\pm$5\%: " +
           (r"the reduced model reproduces the full one, although only just within the threshold" if d["eajuste_med"] > 0.4 else r"the reduced model reproduces the full one") + rf", with guarantee {LEVEL[lv]}; robustness {PATTERN[pt]}.")
    lean = (f" The model was not verified in Lean because {NOT_VERIFIED[s]}." if s in NOT_VERIFIED
            else r" The hypotheses on the dynamics were verified in Lean (\sref{models}).")
    L.append(head + " " + sel + roles + " " + met)
    L.append("")
    L.append(validation(s, d) + lean)
    return L


def main():
    systems = sorted(SEL, key=str.lower)
    assert set(systems) == set(TXT), set(systems) ^ set(TXT)
    L = [r"\snote{systems}", "",
         r"This note summarises, for each of the 34 benchmark problems, what the model describes, which parameters the method selected and what they mean in the model, "
         r"how well the reduced model reproduces the full one, and how it predicted held-out data. The meaning of each selected parameter was taken from the reactions and rules of the SBML model in which it appears "
         r"(following assignment rules and condition-specific parameters to the reactions they affect). "
         r"The numbers are those of Table~1 of the main text and Supplementary Table~\ref{tab:selected}: $p$ is the number of estimated parameters, "
         r"$\kappa$ and VIF are the condition number and largest variance inflation factor of the selected sensitivity columns, $R_{\mathrm{var}}$ is the fraction of sensitivity energy kept, "
         r"$\cos\Delta$ and $e_{\mathrm{fit}}$ are medians over 15 random scenarios at $\pm$5\% (threshold $\tau_e=0.436$), the level of guarantee is defined in the Results of the main text, "
         r"and the robustness patterns A--D are those of Fig.~4 of the main text. In the external validation, both the reduced and the full model are refitted to the training data, and the test $\chi^2/n$ "
         r"(mean squared residual divided by the recorded noise variance; about 1 for a model that predicts within the noise) is computed on the held-out data. The published estimate $\\theta_0$ was obtained with all the data, including the test data, so its test $\\chi^2/n$ is a reference rather than a competing prediction.", ""]
    for s in systems:
        L += paragraph(s) + [""]
    txt = "\n".join(L) + "\n"
    assert all(ord(c) < 128 for c in txt), [c for c in txt if ord(c) >= 128][:5]
    (HERE / "suppl_systems.tex").write_text(txt)
    print("suppl_systems.tex:", len(systems), "systems,", len(txt.split()), "words")


if __name__ == "__main__":
    main()
