// initialization

const RESPONSIVE_WIDTH = 1024

let headerWhiteBg = false
let isHeaderCollapsed = window.innerWidth < RESPONSIVE_WIDTH
const collapseBtn = document.getElementById("collapse-btn")
const collapseHeaderItems = document.getElementById("collapsed-header-items")



function onHeaderClickOutside(e) {

    if (!collapseHeaderItems.contains(e.target)) {
        toggleHeader()
    }

}


function toggleHeader() {
    if (isHeaderCollapsed) {
        // collapseHeaderItems.classList.remove("max-md:tw-opacity-0")
        collapseHeaderItems.classList.add("opacity-100",)
        collapseHeaderItems.style.width = "60vw"
        collapseBtn.classList.remove("bi-list")
        collapseBtn.classList.add("bi-x", "max-lg:tw-fixed")
        isHeaderCollapsed = false

        setTimeout(() => window.addEventListener("click", onHeaderClickOutside), 1)

    } else {
        collapseHeaderItems.classList.remove("opacity-100")
        collapseHeaderItems.style.width = "0vw"
        collapseBtn.classList.remove("bi-x", "max-lg:tw-fixed")
        collapseBtn.classList.add("bi-list")
        isHeaderCollapsed = true
        window.removeEventListener("click", onHeaderClickOutside)

    }
}

function responsive() {
    if (window.innerWidth > RESPONSIVE_WIDTH) {
        collapseHeaderItems.style.width = ""

    } else {
        isHeaderCollapsed = true
    }
}

window.addEventListener("resize", responsive)

function closeMobileNav() {
    if (!isHeaderCollapsed && window.innerWidth < RESPONSIVE_WIDTH) {
        toggleHeader()
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".header-links, header a[href*='#']").forEach((link) => {
        link.addEventListener("click", () => closeMobileNav())
    })
})

/**
 * Demo templates — add new entries here; dropdown updates automatically.
 */
const DEMO_TEMPLATES = [
    {value: "", label: "Auto (from research category)"},
    {value: "gym-modern", label: "Gym Classic"},
    {value: "gym-modern-dark", label: "Gym Modern-Dark"},
    {value: "salon-modern", label: "Salon Classic"},
    {value: "salon-aesthetic", label: "Salon Aesthetic"},
    {value: "salon-chocolate", label: "Salon Chocolate Luxury"},
    {value: "retail-modern", label: "Retail Modern"},
]

const PIPELINE_STEP_ORDER = [
    "lead_finder",
    "step_research",
    "step_build",
    "step_publish",
    "pitches",
]

const STEP_SKILL_PREFIX = {
    lead_finder: "[lead-finder]",
    research: "[lead-research]",
    demo_build: "[build_demo.py]",
    demo_publish: "[publish]",
    pitch: "[pitch-generator]",
}

/**
 * Hermes app shell hooks (placeholder wiring)
 */
function hermesShellInit() {
    const btn = document.getElementById("btn_run_leads")
    const out = document.getElementById("lf_out")
    const leadResults = document.getElementById("lead_results")
    const city = document.getElementById("lf_city")
    const category = document.getElementById("lf_category")
    const kpiResearch = document.getElementById("kpi_research_count")
    const kpiDemos = document.getElementById("kpi_demos_count")
    const listResearch = document.getElementById("list_research")
    const listDemos = document.getElementById("list_demos")
    const selectedLeadEl = document.getElementById("selected_lead")
    const currentSlugEl = document.getElementById("current_slug")
    const slugCountEl = document.getElementById("slug_count")
    const workflowStatusEl = document.getElementById("workflow_status")
    const btnResearch2 = document.getElementById("btn_run_research2")
    const researchLeadSelect = document.getElementById("research_lead_select")
    const leadPickerCountEl = document.getElementById("lead_picker_count")
    const stepResearchEl = document.getElementById("step_research")
    const btnBuild = document.getElementById("btn_build_demo")
    const btnPublish = document.getElementById("btn_publish_demo")
    const btnPitch = document.getElementById("btn_generate_pitch")
    const inBusiness = document.getElementById("in_business")
    const inCity = document.getElementById("in_city")
    const inCategory = document.getElementById("in_category")
    const inSlug = document.getElementById("in_slug")
    const slugSelect = document.getElementById("slug_select")
    const btnFillSlugFromSelected = document.getElementById("btn_fill_slug_from_selected")
    const templateSelect = document.getElementById("template_select")
    const btnRefreshState = document.getElementById("btn_refresh_state")
    const pipelineStepper = document.getElementById("pipeline_stepper")
    const pipelineWorkspace = document.getElementById("pipeline")
    const pipelineModeDesc = document.getElementById("pipeline_mode_desc")
    const agentActivityPanel = document.getElementById("agent_activity_panel")
    const agentKpiLeads = document.getElementById("agent_kpi_leads")
    const agentKpiDemos = document.getElementById("agent_kpi_demos")
    const agentKpiPublished = document.getElementById("agent_kpi_published")
    const badgeStep1 = document.getElementById("badge_step1")
    const stepBuildEl = document.getElementById("step_build")
    const stepPublishEl = document.getElementById("step_publish")
    const pitchesEl = document.getElementById("pitches")

    const STEP_FEED_IDS = {
        lead_finder: "step_feed_lead_finder",
        research: "step_feed_research",
        demo_build: "step_feed_demo_build",
        demo_publish: "step_feed_publish",
        pitch: "step_feed_pitch",
    }

    let lastResearch = []
    let lastDemos = []
    let lastLeads = []
    let selectedLeadIdx = -1
    let activeStepId = "lead_finder"
    let pipelineMode = "guided"

    function getSlug() {
        const fromInput = (inSlug?.value || "").trim()
        if (fromInput) return fromInput
        const fromSelect = (slugSelect?.value || "").trim()
        if (fromSelect) return fromSelect
        return guessSlugFromLead(selectedLead)
    }

    function getStepCompletionState() {
        const slug = getSlug()
        const hasLeads = lastLeads.length > 0
        const hasResearch = Boolean(slug && lastResearch.some((r) => r.slug === slug))
        const demoMeta = slug ? lastDemos.find((d) => d.slug === slug) : null
        const hasDemo = Boolean(demoMeta)
        const hasPublished = Boolean(demoMeta?.demo_url)
        return {
            lead_finder: hasLeads,
            step_research: hasResearch,
            step_build: hasDemo,
            step_publish: hasPublished,
            pitches: false,
        }
    }

    function getUnlockedStepIndex() {
        const state = getStepCompletionState()
        let max = 0
        if (state.lead_finder) max = Math.max(max, 1)
        if (state.step_research) max = Math.max(max, 2)
        if (state.step_build) max = Math.max(max, 3)
        if (state.step_publish) max = Math.max(max, 4)
        if (state.pitches) max = Math.max(max, 5)
        return max
    }

    function setPipelineMode(mode) {
        pipelineMode = mode === "explorer" ? "explorer" : "guided"
        if (pipelineWorkspace) {
            pipelineWorkspace.classList.toggle("pipeline-mode-guided", pipelineMode === "guided")
            pipelineWorkspace.classList.toggle("pipeline-mode-explorer", pipelineMode === "explorer")
        }
        document.querySelectorAll("[data-pipeline-mode]").forEach((btn) => {
            const on = btn.getAttribute("data-pipeline-mode") === pipelineMode
            btn.classList.toggle("is-active", on)
            btn.setAttribute("aria-selected", on ? "true" : "false")
        })
        if (pipelineModeDesc) {
            pipelineModeDesc.textContent =
                pipelineMode === "guided"
                    ? "Guided flow — complete each step to unlock the next. Live agent output on the right."
                    : "All steps — jump to any step. Live agent activity stays on the right."
        }
        updateGuidedCards()
    }

    function updateStepCardBadges(state) {
        const labels = {
            lead_finder: state.lead_finder ? "Done" : "Ready",
            step_research: state.step_research ? "Done" : "Pending",
            step_build: state.step_build ? "Done" : "Pending",
            step_publish: state.step_publish ? "Done" : "Pending",
            pitches: "Pending",
        }
        if (badgeStep1 && lastLeads.length) {
            badgeStep1.textContent = `${lastLeads.length} leads`
        }
        PIPELINE_STEP_ORDER.forEach((id) => {
            const card = document.getElementById(id)
            if (!card) return
            const badge = card.querySelector(".step-card-badge")
            if (badge && id !== "lead_finder") badge.textContent = labels[id] || "Pending"
            card.classList.toggle("is-done", Boolean(state[id]))
        })
    }

    function updateGuidedCards() {
        const unlockedIdx = getUnlockedStepIndex()
        PIPELINE_STEP_ORDER.forEach((id, idx) => {
            const card = document.getElementById(id)
            if (!card) return
            const unlocked = idx <= unlockedIdx
            card.classList.toggle("is-unlocked", unlocked)
            const isActive = id === activeStepId
            card.classList.toggle("is-active", isActive)
            if (pipelineMode === "guided") {
                const isDone = card.classList.contains("is-done")
                card.classList.toggle("is-collapsed", isDone && !isActive)
            } else {
                card.classList.remove("is-collapsed")
            }
        })
    }

    function advanceGuidedStep(nextStepId) {
        if (pipelineMode !== "guided") return
        activeStepId = nextStepId
        updateGuidedCards()
        updatePipelineStepper()
        const el = document.getElementById(nextStepId)
        if (el) el.scrollIntoView({behavior: "smooth", block: "start"})
    }

    function scrollToStep(stepId, {mode = null} = {}) {
        if (mode) setPipelineMode(mode)
        const el = document.getElementById(stepId)
        if (!el) return
        activeStepId = stepId
        if (pipelineMode === "guided") {
            const idx = PIPELINE_STEP_ORDER.indexOf(stepId)
            if (idx >= 0) {
                PIPELINE_STEP_ORDER.forEach((id, i) => {
                    const card = document.getElementById(id)
                    if (card) card.classList.toggle("is-unlocked", i <= Math.max(idx, getUnlockedStepIndex()))
                })
            }
        }
        el.scrollIntoView({behavior: "smooth", block: "start"})
        updatePipelineStepper()
        updateGuidedCards()
    }

    function updatePipelineStepper() {
        if (!pipelineStepper) return
        const state = getStepCompletionState()
        const slug = getSlug()
        const hasLeads = lastLeads.length > 0
        const hasResearch = Boolean(slug && lastResearch.some((r) => r.slug === slug))
        const demoMeta = slug ? lastDemos.find((d) => d.slug === slug) : null
        const hasDemo = Boolean(demoMeta)
        const hasPublished = Boolean(demoMeta?.demo_url)

        const stepState = state

        const order = PIPELINE_STEP_ORDER
        let suggested = "lead_finder"
        if (hasLeads && !hasResearch) suggested = "step_research"
        else if (hasResearch && !hasDemo) suggested = "step_build"
        else if (hasDemo && !hasPublished) suggested = "step_publish"
        else if (hasDemo) suggested = "pitches"

        pipelineStepper.querySelectorAll("[data-goto]").forEach((btn) => {
            const id = btn.getAttribute("data-goto") || ""
            btn.classList.toggle("is-done", Boolean(stepState[id]))
            btn.classList.toggle("is-active", id === activeStepId || (!activeStepId && id === suggested))
        })

        updateStepCardBadges(stepState)
        updateGuidedCards()

        if (agentKpiLeads) agentKpiLeads.textContent = String(lastLeads.length)
        if (agentKpiDemos) agentKpiDemos.textContent = String(lastDemos.length)
        if (agentKpiPublished) {
            agentKpiPublished.textContent = String(lastDemos.filter((d) => d.demo_url).length)
        }
    }

    function initPipelineNav() {
        document.querySelectorAll("[data-pipeline-mode]").forEach((btn) => {
            btn.addEventListener("click", () => {
                setPipelineMode(btn.getAttribute("data-pipeline-mode") || "guided")
            })
        })

        if (pipelineStepper) {
            pipelineStepper.querySelectorAll("[data-goto]").forEach((btn) => {
                btn.addEventListener("click", () => {
                    const id = btn.getAttribute("data-goto")
                    if (id) scrollToStep(id, {mode: "explorer"})
                })
            })
        }

        document.querySelectorAll(".workflow-jump[data-goto]").forEach((card) => {
            const go = () => {
                const id = card.getAttribute("data-goto")
                if (id) scrollToStep(id, {mode: "explorer"})
            }
            card.addEventListener("click", go)
            card.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault()
                    go()
                }
            })
        })

        PIPELINE_STEP_ORDER.forEach((id) => {
            const card = document.getElementById(id)
            const header = card?.querySelector(".step-card-header")
            if (!header) return
            header.addEventListener("click", () => {
                activeStepId = id
                if (pipelineMode === "guided") {
                    card.classList.remove("is-collapsed")
                    updateGuidedCards()
                }
                scrollToStep(id)
            })
        })

        if (btnRefreshState) {
            btnRefreshState.addEventListener("click", () => {
                setButtonBusy(btnRefreshState, true, "Refreshing…")
                refreshState().finally(() => setButtonBusy(btnRefreshState, false))
            })
        }

        if (city) {
            city.addEventListener("keydown", (e) => {
                if (e.key === "Enter") btn?.click()
            })
        }
        if (category) {
            category.addEventListener("keydown", (e) => {
                if (e.key === "Enter") btn?.click()
            })
        }

        function applyHashMode() {
            const raw = (location.hash || "").replace("#", "")
            if (raw === "pipeline-guided") {
                setPipelineMode("guided")
                scrollToStep("lead_finder")
                return
            }
            if (raw === "pipeline") {
                setPipelineMode("explorer")
                pipelineWorkspace?.scrollIntoView({behavior: "smooth", block: "start"})
                return
            }
            if (PIPELINE_STEP_ORDER.includes(raw)) {
                setPipelineMode("explorer")
                scrollToStep(raw)
            }
        }

        window.addEventListener("hashchange", applyHashMode)
        applyHashMode()
        if (!location.hash) setPipelineMode("guided")
    }

    function normalizeLead(raw, fallbackCity = "", fallbackCategory = "") {
        if (!raw || typeof raw !== "object") return null
        const business = (
            raw.business ||
            raw.business_name ||
            raw.name ||
            ""
        ).trim()
        if (!business) return null
        const city = (raw.city || raw.address_city || fallbackCity || "").trim()
        const category = (raw.category || fallbackCategory || "").trim()
        const score = raw.opportunity_score ?? raw.score
        return {
            ...raw,
            business,
            city,
            category,
            opportunity_score: score,
            issues: raw.issues || raw.issues_found || [],
            slug: raw.slug || "",
        }
    }

    function extractLeadsFromResult(result, fallbackCity = "", fallbackCategory = "") {
        if (!result) return []
        let raw = []
        if (Array.isArray(result)) raw = result
        else if (Array.isArray(result.leads)) raw = result.leads
        else if (result.data && Array.isArray(result.data.leads)) raw = result.data.leads
        const meta = result.meta || {}
        const city = fallbackCity || meta.city || ""
        const category = fallbackCategory || meta.category || ""
        return raw.map((r) => normalizeLead(r, city, category)).filter(Boolean)
    }

    function fillResearchInputsFromLead(lead) {
        if (!lead) return
        if (inBusiness) inBusiness.value = lead.business || ""
        if (inCity) inCity.value = lead.city || ""
        if (inCategory) inCategory.value = lead.category || ""
    }

    function populateResearchLeadPicker(leads) {
        if (!researchLeadSelect) return
        const currentIdx = selectedLeadIdx
        researchLeadSelect.innerHTML = ""
        const placeholder = document.createElement("option")
        placeholder.value = ""
        placeholder.textContent = leads.length
            ? "Choose a business to research…"
            : "Run lead finder first, then pick a business…"
        researchLeadSelect.appendChild(placeholder)

        leads.forEach((l, idx) => {
            const opt = document.createElement("option")
            opt.value = String(idx)
            const score = l.opportunity_score != null ? ` • score ${l.opportunity_score}/10` : ""
            const meta = [l.city, l.category].filter(Boolean).join(", ")
            opt.textContent = meta ? `${l.business} (${meta})${score}` : `${l.business}${score}`
            researchLeadSelect.appendChild(opt)
        })

        if (leadPickerCountEl) {
            leadPickerCountEl.textContent = leads.length ? `(${leads.length} found)` : ""
        }

        if (currentIdx >= 0 && currentIdx < leads.length) {
            researchLeadSelect.value = String(currentIdx)
        }
    }

    function selectLeadByIndex(idx, {scrollToStep2 = false} = {}) {
        if (idx < 0 || idx >= lastLeads.length) return
        selectedLeadIdx = idx
        const lead = lastLeads[idx]
        setSelectedLead(lead)
        fillResearchInputsFromLead(lead)
        if (researchLeadSelect) researchLeadSelect.value = String(idx)
        renderLeadResults(lastLeads)
        setStatus(`Selected: ${lead.business}. Review fields below, then Run research.`)
        if (scrollToStep2) {
            advanceGuidedStep("step_research")
        }
        activeStepId = scrollToStep2 ? "step_research" : "lead_finder"
        updatePipelineStepper()
    }

    function updateCurrentSlugDisplay() {
        const slug = getSlug()
        if (currentSlugEl) currentSlugEl.textContent = slug || "—"
    }

    function setSlugValue(slug) {
        const s = (slug || "").trim()
        if (inSlug) inSlug.value = s
        if (slugSelect) {
            const hasOption = s && Array.from(slugSelect.options).some((o) => o.value === s)
            slugSelect.value = hasOption ? s : ""
        }
        updateCurrentSlugDisplay()
    }

    function appendSlugOption(slug, label) {
        const opt = document.createElement("option")
        opt.value = slug
        opt.textContent = label
        slugSelect.appendChild(opt)
    }

    function populateSlugDropdown(research, demos) {
        if (!slugSelect) return
        const current = getSlug()
        const demoSlugs = new Set((demos || []).map((d) => d.slug).filter(Boolean))
        const seen = new Set()

        slugSelect.innerHTML = ""
        const placeholder = document.createElement("option")
        placeholder.value = ""
        placeholder.textContent = "Choose existing slug…"
        slugSelect.appendChild(placeholder)

        for (const r of research || []) {
            const slug = (r.slug || "").trim()
            if (!slug || seen.has(slug)) continue
            seen.add(slug)
            const label = r.business
                ? `${slug} — ${r.business}${r.city ? ` (${r.city})` : ""}`
                : slug
            const tag = demoSlugs.has(slug) ? " • demo built" : ""
            appendSlugOption(slug, `${label}${tag}`)
        }

        for (const d of demos || []) {
            const slug = (d.slug || "").trim()
            if (!slug || seen.has(slug)) continue
            seen.add(slug)
            appendSlugOption(slug, `${slug} (demo only)`)
        }

        if (slugCountEl) {
            const n = seen.size
            slugCountEl.textContent = n ? `(${n} saved)` : "(none yet)"
        }

        if (current && seen.has(current)) setSlugValue(current)
        else updateCurrentSlugDisplay()
    }

    function populateTemplateSelect() {
        if (!templateSelect) return
        const current = templateSelect.value
        templateSelect.innerHTML = ""
        for (const t of DEMO_TEMPLATES) {
            const opt = document.createElement("option")
            opt.value = t.value
            opt.textContent = t.label
            templateSelect.appendChild(opt)
        }
        const hasCurrent = DEMO_TEMPLATES.some((t) => t.value === current)
        if (hasCurrent) templateSelect.value = current
    }

    function getSelectedTemplate() {
        return (templateSelect?.value || "").trim()
    }

    async function refreshState() {
        try {
            const res = await fetch("/api/pipeline/state")
            const data = await res.json()
            if (!data || !data.ok) return

            lastResearch = data.research || []
            lastDemos = data.demos || []

            if (kpiResearch) kpiResearch.textContent = String(data.counts?.research ?? 0)
            if (kpiDemos) kpiDemos.textContent = String(data.counts?.demos ?? 0)

            if (listResearch) {
                const rows = (data.research || []).slice(0, 8).map((r) => {
                    const title = r.business ? `${r.business}` : r.slug
                    const meta = [r.city, r.category].filter(Boolean).join(" • ")
                    return `<li>
                        <button type="button" data-research-slug="${r.slug}" class="tw-w-full tw-text-left tw-flex tw-flex-col tw-gap-1 tw-rounded-md tw-bg-black/20 tw-border tw-border-white/10 tw-p-3 hover:tw-border-white/30">
                            <div class="tw-font-semibold">${title}</div>
                            <div class="tw-text-xs tw-text-gray-400">${meta || "research"} • ${r.slug}</div>
                        </button>
                    </li>`
                })
                listResearch.innerHTML = rows.join("") || `<li class="tw-text-sm tw-text-gray-400">No research saved yet.</li>`
                listResearch.querySelectorAll("[data-research-slug]").forEach((el) => {
                    el.addEventListener("click", () => {
                        const slug = el.getAttribute("data-research-slug") || ""
                        if (slug) {
                            setSlugValue(slug)
                            setStatus(`Slug set from research: ${slug}`)
                        }
                    })
                })
            }

            if (listDemos) {
                const rows = (data.demos || []).slice(0, 8).map((d) => {
                    const url = d.demo_url ? `<a class="tw-text-secondary" href="${d.demo_url}" target="_blank" rel="noreferrer">open</a>` : ""
                    const tpl = d.template_used ? ` • ${d.template_used}` : ""
                    return `<li class="tw-flex tw-items-center tw-justify-between tw-rounded-md tw-bg-black/20 tw-border tw-border-white/10 tw-p-3">
                        <button type="button" data-demo-slug="${d.slug}" class="tw-flex-1 tw-text-left hover:tw-opacity-80">
                            <div class="tw-font-semibold">${d.slug}</div>
                            <div class="tw-text-xs tw-text-gray-400">demo${tpl}</div>
                        </button>
                        <div class="tw-text-sm">${url}</div>
                    </li>`
                })
                listDemos.innerHTML = rows.join("") || `<li class="tw-text-sm tw-text-gray-400">No demos built yet.</li>`
                listDemos.querySelectorAll("[data-demo-slug]").forEach((el) => {
                    el.addEventListener("click", () => {
                        const slug = el.getAttribute("data-demo-slug") || ""
                        if (slug) {
                            setSlugValue(slug)
                            setStatus(`Slug set from demo: ${slug}`)
                        }
                    })
                })
            }

            populateSlugDropdown(data.research, data.demos)
            updatePipelineStepper()
        } catch {
            // ignore
        }
    }

    let selectedLead = null

    function setStatus(msg) {
        if (workflowStatusEl) workflowStatusEl.textContent = msg
    }

    function scrollToAgentLog() {
        if (agentActivityPanel) {
            agentActivityPanel.scrollIntoView({behavior: "smooth", block: "nearest"})
        }
        if (out) out.scrollTop = out.scrollHeight
    }

    function appendAgentLine(line, stepKey = null) {
        if (!out) return
        const prefix = stepKey && STEP_SKILL_PREFIX[stepKey] ? STEP_SKILL_PREFIX[stepKey] + " " : ""
        const text = String(line ?? "").trim()
        if (!text) return
        out.textContent += `${prefix}${text}\n`
        out.scrollTop = out.scrollHeight
    }

    function initStepFeedButtons() {
        document.querySelectorAll("[data-scroll-log]").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                e.preventDefault()
                scrollToAgentLog()
            })
        })
    }

    function pickPreviewLines(lines, max = 4) {
        const useful = (lines || [])
            .map((l) => String(l ?? "").trim())
            .filter((s) => s && s !== "json" && !s.startsWith("$") && !/^\[exit\]/.test(s))
        return useful.slice(-max)
    }

    function setStepFeed(stepKey, {phase = "idle", message = "—", preview = []} = {}) {
        const el = document.getElementById(STEP_FEED_IDS[stepKey] || "")
        if (!el) return
        el.classList.remove("tw-hidden", "is-running", "is-done", "is-error")
        if (phase === "idle") el.classList.add("tw-hidden")
        if (phase === "running") el.classList.add("is-running")
        if (phase === "done") el.classList.add("is-done")
        if (phase === "error") el.classList.add("is-error")

        const statusEl = el.querySelector(".step-feed-status")
        const msgEl = el.querySelector(".step-feed-message")
        const preEl = el.querySelector(".step-feed-preview")
        const labels = {
            idle: "Idle",
            running: "Running…",
            done: "Done",
            error: "Error",
        }
        if (statusEl) {
            statusEl.textContent = labels[phase] || phase
            statusEl.classList.remove("is-running", "is-done", "is-error")
            if (phase === "running") statusEl.classList.add("is-running")
            if (phase === "done") statusEl.classList.add("is-done")
            if (phase === "error") statusEl.classList.add("is-error")
        }
        if (msgEl) msgEl.textContent = message
        if (preEl) {
            const lines = preview || []
            if (lines.length) {
                preEl.textContent = lines.join("\n")
                preEl.classList.remove("tw-hidden")
            } else {
                preEl.textContent = ""
                preEl.classList.add("tw-hidden")
            }
        }
    }

    function setButtonBusy(btn, busy, busyLabel = "Running…") {
        if (!btn) return
        if (busy) {
            if (!btn.dataset.prevLabel) btn.dataset.prevLabel = btn.textContent || ""
            btn.disabled = true
            btn.textContent = busyLabel
            btn.classList.add("tw-opacity-70")
        } else {
            btn.disabled = false
            if (btn.dataset.prevLabel) btn.textContent = btn.dataset.prevLabel
            btn.classList.remove("tw-opacity-70")
        }
    }

    function guessSlugFromLead(lead) {
        if (lead?.slug) return String(lead.slug).trim()
        const biz = (lead?.business || "").trim().toLowerCase()
        if (biz) {
            const match = lastResearch.find((r) => (r.business || "").trim().toLowerCase() === biz)
            if (match?.slug) return match.slug
        }
        const s = (lead?.business || "").toLowerCase().trim()
        return s.replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")
    }

    function setSelectedLead(lead) {
        selectedLead = lead
        if (!selectedLeadEl) return
        if (!lead) {
            selectedLeadEl.textContent = "None"
            selectedLeadIdx = -1
            if (researchLeadSelect) researchLeadSelect.value = ""
            updateCurrentSlugDisplay()
            return
        }
        const title = lead.business || lead.slug || "Lead"
        const meta = [lead.city, lead.category].filter(Boolean).join(" • ")
        const score = lead.opportunity_score != null ? ` • score ${lead.opportunity_score}/10` : ""
        selectedLeadEl.textContent = meta ? `${title} (${meta})${score}` : `${title}${score}`

        const slug = guessSlugFromLead(lead)
        if (slug) setSlugValue(slug)
        else updateCurrentSlugDisplay()
    }

    function fillSlugInputFromSelected() {
        if (!selectedLead) {
            setStatus("Select a lead first.")
            return
        }
        const slug = guessSlugFromLead(selectedLead)
        setSlugValue(slug)
        setStatus(slug ? `Slug set: ${slug}` : "Could not derive slug.")
    }

    function renderLeadResults(leads) {
        if (!leadResults) return
        lastLeads = leads
        populateResearchLeadPicker(leads)
        if (!Array.isArray(leads) || leads.length === 0) {
            leadResults.innerHTML = `<div class="tw-text-sm tw-text-gray-400">No leads found. Try a different city/category.</div>`
            return
        }
        leadResults.innerHTML = leads
            .slice(0, 12)
            .map((l, idx) => {
                const title = l.business || l.slug || `Lead ${idx + 1}`
                const meta = [l.city, l.category].filter(Boolean).join(" • ")
                const score = l.opportunity_score != null ? `<span class="tw-text-secondary">Score ${l.opportunity_score}/10</span>` : ""
                const issues = Array.isArray(l.issues) ? l.issues.slice(0, 2).join(", ") : ""
                const selected = idx === selectedLeadIdx
                const border = selected ? "tw-border-secondary tw-bg-secondary/10" : "tw-border-white/10"
                return `<button type="button" data-lead-idx="${idx}" class="tw-text-left tw-rounded-md tw-bg-black/20 tw-border ${border} tw-p-3 hover:tw-border-white/30">
                    <div class="tw-flex tw-items-center tw-justify-between tw-gap-2">
                        <div class="tw-font-semibold">${title}</div>
                        ${score}
                    </div>
                    <div class="tw-text-xs tw-text-gray-400">${meta || ""}</div>
                    ${issues ? `<div class="tw-mt-2 tw-text-xs tw-text-gray-300">Issues: ${issues}</div>` : ""}
                    ${selected ? `<div class="tw-mt-2 tw-text-xs tw-text-secondary">Selected → Step 2</div>` : ""}
                </button>`
            })
            .join("")

        leadResults.querySelectorAll("[data-lead-idx]").forEach((el) => {
            el.addEventListener("click", () => {
                const i = Number(el.getAttribute("data-lead-idx") || "0")
                selectLeadByIndex(i, {scrollToStep2: true})
                activeStepId = "step_research"
                updatePipelineStepper()
            })
        })
    }

    async function startRun(kind, payload) {
        const res = await fetch("/api/pipeline/run/start", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({kind, ...payload}),
        })
        return await res.json()
    }

    async function streamRun(runId, {stepKey = null, runningMessage = "Running…"} = {}) {
        let offset = 0
        let done = false
        const started = Date.now()
        const allDisplayLines = []

        if (stepKey) {
            setStepFeed(stepKey, {phase: "running", message: runningMessage, preview: []})
        }
        if (out) out.classList.add("is-running")

        // Filter out raw JSON blocks from Hermes output
        let jsonLikely = false
        let jsonDepth = 0
        const filterDisplayLines = (incoming) => {
            const outLines = []
            for (const line of incoming) {
                const t = String(line ?? "")
                const s = t.trim()
                if (!jsonLikely && s === "json") {
                    jsonLikely = true
                    continue
                }
                if (jsonLikely && jsonDepth === 0 && (s.startsWith("{") || s.startsWith("["))) {
                    for (const ch of t) {
                        if (ch === "{" || ch === "[") jsonDepth += 1
                        else if (ch === "}" || ch === "]") jsonDepth = Math.max(0, jsonDepth - 1)
                    }
                    continue
                }
                if (jsonDepth > 0) {
                    for (const ch of t) {
                        if (ch === "{" || ch === "[") jsonDepth += 1
                        else if (ch === "}" || ch === "]") jsonDepth = Math.max(0, jsonDepth - 1)
                    }
                    if (jsonDepth === 0) jsonLikely = false
                    continue
                }
                if (jsonLikely && s.length > 0) jsonLikely = false
                outLines.push(t)
            }
            return outLines
        }

        let lastRun = null

        while (!done && Date.now() - started < 300000) {
            const r = await fetch(`/api/pipeline/run/${runId}?offset=${offset}`)
            const d = await r.json()
            if (d?.ok) {
                lastRun = d.run
                const lines = Array.isArray(d.logs) ? d.logs : []
                if (lines.length && out) {
                    const display = filterDisplayLines(lines)
                    if (display.length) {
                        display.forEach((line) => appendAgentLine(line, stepKey))
                        allDisplayLines.push(...display)
                    }
                }
                if (stepKey && allDisplayLines.length) {
                    setStepFeed(stepKey, {
                        phase: "running",
                        message: runningMessage,
                        preview: pickPreviewLines(allDisplayLines),
                    })
                }
                offset = d.next_offset || offset
                const status = d.run?.status
                if (status === "done" || status === "error") done = true
            }
            if (!done) await new Promise((resolve) => setTimeout(resolve, 800))
        }

        if (out) out.classList.remove("is-running")

        if (stepKey) {
            const preview = pickPreviewLines(allDisplayLines)
            const ok = lastRun?.status === "done"
            const exitCode = lastRun?.exit_code
            let doneMsg = runningMessage.replace(/…$/, "")
            if (ok) {
                doneMsg = `${doneMsg} finished successfully.`
                if (lastRun?.result_json?.url) doneMsg = `Published: ${lastRun.result_json.url}`
            } else {
                const tail = preview[preview.length - 1] || `Exit code ${exitCode ?? "?"}`
                doneMsg = `${doneMsg} failed — ${tail}`
            }
            setStepFeed(stepKey, {
                phase: ok ? "done" : "error",
                message: doneMsg,
                preview,
            })
        }

        return lastRun
    }

    if (!btn || !out || !city || !category) {
        populateTemplateSelect()
        initStepFeedButtons()
        initPipelineNav()
        setPipelineMode("guided")
        refreshState()
        return
    }

    initPipelineNav()
    initStepFeedButtons()
    setPipelineMode(location.hash === "#pipeline" ? "explorer" : "guided")

    btn.addEventListener("click", async () => {
        const payload = {
            city: (city.value || "").trim(),
            category: (category.value || "").trim(),
        }

        out.textContent = ""
        appendAgentLine(`scanning ${payload.city || "…"}…`, "lead_finder")
        setStepFeed("lead_finder", {phase: "running", message: "Starting lead finder…", preview: []})
        setButtonBusy(btn, true, "Finding leads…")
        try {
            const data = await startRun("lead_finder", payload)

            if (data?.needs_input) {
                out.textContent = data.prompt || "Please enter city and category."

                // UX: bring user to inputs + highlight missing
                const missing = new Set(Array.isArray(data.missing) ? data.missing : [])
                const leadCard = document.getElementById("lead_finder")
                if (leadCard) leadCard.scrollIntoView({behavior: "smooth", block: "start"})

                const errCls = "is-error"
                const clearErr = (el) => {
                    if (!el) return
                    el.classList.remove(errCls)
                }
                const setErr = (el) => {
                    if (!el) return
                    el.classList.add(errCls)
                }

                if (missing.has("city")) setErr(city)
                else clearErr(city)
                if (missing.has("category")) setErr(category)
                else clearErr(category)

                const focusEl = missing.has("city") ? city : missing.has("category") ? category : city
                if (focusEl && typeof focusEl.focus === "function") focusEl.focus()
                return
            }

            if (!data?.ok || !data?.run_id) {
                out.textContent = data?.error ? `Lead finder failed: ${data.error}` : "Lead finder failed."
                return
            }

            const runId = data.run_id
            out.textContent = "Running lead finder…\n"
            setStatus("Lead finder running…")
            const finalRun = await streamRun(runId, {
                stepKey: "lead_finder",
                runningMessage: `Finding leads in ${payload.city}…`,
            })
            setStatus(finalRun?.status === "done" ? "Lead finder done." : "Lead finder finished with error.")

            const finderCity = (city.value || "").trim()
            const finderCategory = (category.value || "").trim()
            const leads = extractLeadsFromResult(finalRun?.result_json, finderCity, finderCategory)
            if (leads.length) {
                selectedLeadIdx = -1
                renderLeadResults(leads)
                activeStepId = "lead_finder"
                setStatus(`${leads.length} leads found — pick one to continue.`)
                updatePipelineStepper()
                advanceGuidedStep("step_research")
            } else if (finalRun?.status === "done") {
                setStatus("Lead finder finished but no structured leads parsed. Check log output.")
            }
            refreshState()
        } catch (e) {
            out.textContent = "Lead finder error.\n"
            setStepFeed("lead_finder", {phase: "error", message: "Lead finder error.", preview: []})
        } finally {
            setButtonBusy(btn, false)
        }
    })

    // Step 2: research selected lead
    async function runResearch(payloadOverride) {
        const business = (payloadOverride?.business || inBusiness?.value || selectedLead?.business || "").trim()
        const cityVal = (payloadOverride?.city || inCity?.value || selectedLead?.city || "").trim()
        const categoryVal = (payloadOverride?.category || inCategory?.value || selectedLead?.category || "").trim()

        if (!business || !cityVal || !categoryVal) {
            setStatus("Pick a lead from Step 1 (or dropdown in Step 2) first.")
            setStepFeed("research", {phase: "error", message: "Pick a lead from Step 1 first.", preview: []})
            if (stepResearchEl) stepResearchEl.scrollIntoView({behavior: "smooth", block: "start"})
            return
        }

        const payload = {business, city: cityVal, category: categoryVal}
        out.textContent = ""
        appendAgentLine(`saved research JSON for ${business}…`, "research")
        setStatus(`Research running for ${business}…`)
        setButtonBusy(btnResearch2, true, "Researching…")
        setStepFeed("research", {phase: "running", message: `Researching ${business}…`, preview: []})
        try {
        const data = await startRun("research", payload)
        if (!data?.ok || !data?.run_id) {
            setStatus(data?.prompt || "Research failed to start.")
            setStepFeed("research", {phase: "error", message: data?.prompt || "Research failed to start.", preview: []})
            return
        }
        const finalRun = await streamRun(data.run_id, {
            stepKey: "research",
            runningMessage: `Researching ${business}…`,
        })
        setStatus(finalRun?.status === "done" ? `Research saved for ${business}.` : "Research error.")
        if (finalRun?.status === "done") {
            advanceGuidedStep("step_build")
            setStatus(`Research saved. Next: build demo for ${guessSlugFromLead(selectedLead) || business}.`)
        }
        refreshState()
        } finally {
            setButtonBusy(btnResearch2, false)
        }
    }

    // Step 3: build demo for selected lead slug
    async function runBuild() {
        const slug = getSlug()
        if (!slug) {
            setStatus("Need a lead (slug) to build demo.")
            setStepFeed("demo_build", {phase: "error", message: "Enter or select a slug first.", preview: []})
            return
        }
        out.textContent = ""
        appendAgentLine(`template: ${getSelectedTemplate() || "auto"}`, "demo_build")
        setStatus("Demo build running…")
        setButtonBusy(btnBuild, true, "Building…")
        setStepFeed("demo_build", {phase: "running", message: `Building demo for ${slug}…`, preview: []})
        try {
        const data = await startRun("demo_build", {slug, template: getSelectedTemplate()})
        if (!data?.ok || !data?.run_id) {
            setStatus(data?.prompt || "Demo build failed to start.")
            setStepFeed("demo_build", {phase: "error", message: data?.prompt || "Demo build failed to start.", preview: []})
            return
        }
        const finalRun = await streamRun(data.run_id, {
            stepKey: "demo_build",
            runningMessage: `Building demo for ${slug}…`,
        })
        setStatus(finalRun?.status === "done" ? `Demo built: ${slug}` : "Demo build error.")
        if (finalRun?.status === "done") {
            advanceGuidedStep("step_publish")
            setStatus(`Demo built: ${slug}. Next: publish.`)
        }
        refreshState()
        } finally {
            setButtonBusy(btnBuild, false)
        }
    }

    async function runPublish() {
        const slug = getSlug()
        if (!slug) {
            setStatus("Need slug to publish.")
            setStepFeed("demo_publish", {phase: "error", message: "Enter or select a slug first.", preview: []})
            return
        }
        out.textContent = ""
        appendAgentLine(`publishing ${slug}…`, "demo_publish")
        setStatus("Publish running…")
        setButtonBusy(btnPublish, true, "Publishing…")
        setStepFeed("demo_publish", {phase: "running", message: `Publishing ${slug}…`, preview: []})
        try {
        const data = await startRun("demo_publish", {slug})
        if (!data?.ok || !data?.run_id) {
            setStatus(data?.prompt || "Publish failed to start.")
            setStepFeed("demo_publish", {phase: "error", message: data?.prompt || "Publish failed to start.", preview: []})
            return
        }
        const finalRun = await streamRun(data.run_id, {
            stepKey: "demo_publish",
            runningMessage: `Publishing ${slug} to GitHub Pages…`,
        })
        const pubUrl = finalRun?.result_json?.url
        if (finalRun?.status === "done" && pubUrl) {
            setStatus(`Published: ${pubUrl}`)
            appendAgentLine(pubUrl, "demo_publish")
            advanceGuidedStep("pitches")
        } else if (finalRun?.status === "done") {
            setStatus("Published. GitHub Pages may take 1–2 min. Next: generate pitch.")
            advanceGuidedStep("pitches")
        } else {
            setStatus("Publish error.")
        }
        refreshState()
        } finally {
            setButtonBusy(btnPublish, false)
        }
    }

    async function runPitch() {
        const slug = getSlug()
        if (!slug) {
            setStatus("Need slug for pitch.")
            setStepFeed("pitch", {phase: "error", message: "Enter or select a slug first.", preview: []})
            return
        }
        out.textContent = ""
        appendAgentLine(`generating pitch for ${slug}…`, "pitch")
        setStatus("Pitch running…")
        setButtonBusy(btnPitch, true, "Generating…")
        setStepFeed("pitch", {phase: "running", message: `Generating pitch for ${slug}…`, preview: []})
        try {
        const data = await startRun("pitch", {slug})
        if (!data?.ok || !data?.run_id) {
            setStatus(data?.prompt || "Pitch failed to start.")
            setStepFeed("pitch", {phase: "error", message: data?.prompt || "Pitch failed to start.", preview: []})
            return
        }
        const finalRun = await streamRun(data.run_id, {
            stepKey: "pitch",
            runningMessage: `Generating pitch for ${slug}…`,
        })
        setStatus(finalRun?.status === "done" ? "Pitch generated." : "Pitch error.")
        } finally {
            setButtonBusy(btnPitch, false)
        }
    }

    // Bind buttons (some are added later; guard)
    if (btnResearch2) btnResearch2.addEventListener("click", () => runResearch())
    if (researchLeadSelect) {
        researchLeadSelect.addEventListener("change", () => {
            const v = researchLeadSelect.value
            if (!v) return
            selectLeadByIndex(Number(v))
        })
    }
    if (btnBuild) btnBuild.addEventListener("click", () => runBuild())
    if (btnPublish) btnPublish.addEventListener("click", () => runPublish())
    if (btnPitch) btnPitch.addEventListener("click", () => runPitch())
    if (btnFillSlugFromSelected) btnFillSlugFromSelected.addEventListener("click", () => fillSlugInputFromSelected())
    if (templateSelect) {
        templateSelect.addEventListener("change", () => {
            const tpl = getSelectedTemplate()
            const label = DEMO_TEMPLATES.find((t) => t.value === tpl)?.label || tpl
            setStatus(tpl ? `Template: ${label}` : "Template: auto from category")
        })
    }
    if (slugSelect) {
        slugSelect.addEventListener("change", () => {
            if (slugSelect.value) setSlugValue(slugSelect.value)
        })
    }
    if (inSlug) {
        inSlug.addEventListener("input", () => {
            const v = (inSlug.value || "").trim()
            if (slugSelect && v) {
                const match = Array.from(slugSelect.options).some((o) => o.value === v)
                slugSelect.value = match ? v : ""
            } else if (slugSelect && !v) {
                slugSelect.value = ""
            }
            updateCurrentSlugDisplay()
        })
    }

    populateTemplateSelect()
    refreshState()
}

hermesShellInit()


/**
 * Animations
 */

gsap.registerPlugin(ScrollTrigger)


gsap.to(".reveal-up", {
    opacity: 0,
    y: "100%",
})

gsap.to("#dashboard", {
    boxShadow: "0px 15px 25px -5px rgba(170,49,233,0.44021358543417366)",
    duration: 0.3,
    scrollTrigger: {
        trigger: "#hero-section",
        start: "60% 60%",
        end: "80% 80%",
        // markers: true
    }

})


// ------------- reveal section animations ---------------

const sections = gsap.utils.toArray("section")

sections.forEach((sec) => {

    const revealUptimeline = gsap.timeline({paused: true, 
                                            scrollTrigger: {
                                                            trigger: sec,
                                                            start: "10% 80%", // top of trigger hits the top of viewport
                                                            end: "20% 90%",
                                                            // markers: true,
                                                            // scrub: 1,
                                                        }})

    revealUptimeline.to(sec.querySelectorAll(".reveal-up"), {
        opacity: 1,
        duration: 0.8,
        y: "0%",
        stagger: 0.2,
    })


})
