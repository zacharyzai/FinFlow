<template>
  <div class="ff-app-shell">
    <AppSidebar />
    <div style="flex:1;min-width:0;display:flex;flex-direction:column">
      <AppHeader title="Dashboard" />

      <div class="ff-page-content">

        <!-- ── Stat strip ── -->
        <div class="ff-stat-strip">
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Monthly income</div>
            <div class="ff-stat-value">{{ fmt(income) }}</div>
          </div>
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Spent this cycle</div>
            <div class="ff-stat-value">{{ fmt(spentThisCycle) }}</div>
            <div class="ff-stat-meta">{{ spentPct }}% of income · {{ daysElapsed }} days</div>
          </div>
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Safe daily budget</div>
            <div class="ff-stat-value" style="color:var(--good)">{{ fmt(dailyBudget) }}</div>
            <div class="ff-stat-meta">{{ daysRemaining }} days remaining</div>
          </div>
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Health score</div>
            <div class="ff-stat-value">
              {{ store.healthScore ? store.healthScore.score : '…' }}<span style="font-size:14px;color:var(--text-3)">/100</span>
            </div>
            <div class="ff-stat-meta" v-if="store.healthScore">{{ scoreLabel }}</div>
          </div>
        </div>

        <!-- ── Widget grid ── -->
        <div class="ff-widget-grid">

          <!-- Widget 1: Upload & Parsing -->
          <section class="ff-widget">
            <div class="ff-widget-head">
              <div style="display:flex;align-items:center;gap:9px">
                <span class="material-symbols-outlined" style="font-size:20px;color:var(--text)">cloud_upload</span>
                <span class="ff-widget-title">Smart Upload &amp; Parsing</span>
              </div>
            </div>

            <!-- Drop zone — uploads immediately via the shared upload store,
                 then routes to /upload so progress/success is visible there -->
            <div
              class="ff-drop-zone"
              :class="{ 'ff-drop-zone-active': dragOver }"
              role="button"
              tabindex="0"
              @click="fileInput?.click()"
              @keydown.enter="fileInput?.click()"
              @dragover.prevent="dragOver = true"
              @dragleave.prevent="dragOver = false"
              @drop.prevent="onDrop"
            >
              <input ref="fileInput" type="file" accept=".pdf,.csv" class="hidden" @change="onFile" />
              <span class="material-symbols-outlined" style="font-size:30px;color:var(--text-3)">file_upload</span>
              <div style="font:600 13.5px 'IBM Plex Sans';color:var(--text);margin-top:8px">Drop a statement, or <span style="text-decoration:underline;text-underline-offset:2px">browse files</span></div>
              <div style="font:400 11.5px 'IBM Plex Sans';color:var(--text-3);margin-top:4px">PDF or CSV · up to 10 MB</div>
              <div style="display:flex;justify-content:center;gap:7px;margin-top:13px">
                <span class="ff-bank-tag">DBS</span>
                <span class="ff-bank-tag">OCBC</span>
                <span class="ff-bank-tag">UOB</span>
              </div>
            </div>

            <div style="display:flex;align-items:center;gap:7px;margin-top:13px;padding-top:12px;border-top:1px solid var(--border);font:400 11px 'IBM Plex Sans';color:var(--text-3)">
              <span class="material-symbols-outlined" style="font-size:15px">lock</span>
              Raw statement is deleted immediately after parsing.
            </div>
          </section>

          <!-- Widget 2: Health Score -->
          <section class="ff-widget">
            <div class="ff-widget-head">
              <div style="display:flex;align-items:center;gap:9px">
                <span class="material-symbols-outlined" style="font-size:20px;color:var(--text)">monitoring</span>
                <span class="ff-widget-title">Financial Health Score</span>
              </div>
              <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3)">{{ store.healthScore?.month ?? '' }}</div>
            </div>

            <!-- Loading state -->
            <div v-if="!store.healthScore" style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:32px 0">
              <div style="font:400 12px 'IBM Plex Sans';color:var(--text-3)">Analysing with AI…</div>
            </div>

            <div v-else style="display:flex;gap:24px;flex-wrap:wrap;align-items:center">
              <!-- Gauge -->
              <div style="position:relative;width:164px;height:164px;flex-shrink:0;margin:0 auto">
                <svg width="164" height="164" style="transform:rotate(-90deg)">
                  <circle cx="82" cy="82" r="70" fill="none" style="stroke:var(--surface-2)" stroke-width="13"/>
                  <circle cx="82" cy="82" r="70" fill="none" :style="`stroke:${scoreColor}`" stroke-width="13" stroke-linecap="round" stroke-dasharray="439.8" :stroke-dashoffset="scoreOffset"/>
                </svg>
                <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">
                  <div style="font:600 42px 'IBM Plex Mono';letter-spacing:-1.5px;line-height:1;color:var(--text)">{{ store.healthScore.score }}</div>
                  <div style="font:500 11px 'IBM Plex Mono';color:var(--text-3);margin-top:2px">/ 100</div>
                  <div class="ff-score-label" :style="`color:${scoreColor}`">{{ scoreLabel }}</div>
                </div>
              </div>

              <!-- Dimension bars -->
              <div style="flex:1;min-width:200px;display:flex;flex-direction:column;gap:14px">
                <div v-for="dim in dimensions" :key="dim.label">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="display:flex;align-items:center;gap:7px;font:500 12.5px 'IBM Plex Sans';color:var(--text-2)">
                      {{ dim.label }}
                      <span v-if="dim.weakest" class="ff-weakest-badge">Weakest</span>
                    </span>
                    <span style="font:600 12.5px 'IBM Plex Mono';color:var(--text)">{{ dim.score }}/{{ dim.max }}</span>
                  </div>
                  <div class="ff-progress-track">
                    <div class="ff-progress-bar" :style="`width:${dim.pct}%;background:${dim.color}`"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI insight -->
            <div v-if="store.healthScore?.ai_tip" class="ff-insight-box" style="margin-top:18px">
              <span class="material-symbols-outlined" style="font-size:19px;color:var(--brand);flex-shrink:0">auto_awesome</span>
              <div>
                <div style="font:600 10px 'IBM Plex Sans';letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);margin-bottom:3px">AI insight · weakest dimension</div>
                <div style="font:400 12.5px/1.5 'IBM Plex Sans';color:var(--text-2)">{{ store.healthScore.ai_tip }}</div>
              </div>
            </div>
          </section>

          <!-- Widget 3: Analytics (full width) -->
          <section class="ff-widget ff-widget--full">
            <div class="ff-widget-head" style="flex-wrap:wrap;gap:10px">
              <div style="display:flex;align-items:center;gap:9px">
                <span class="material-symbols-outlined" style="font-size:20px;color:var(--text)">bar_chart</span>
                <span class="ff-widget-title">Month-over-Month Analytics</span>
              </div>
            </div>

            <div style="display:flex;gap:28px;flex-wrap:wrap">
              <!-- Bar chart + category breakdown -->
              <div style="flex:2;min-width:340px">
                <div style="position:relative;height:200px;padding-top:18px">
                  <div class="ff-avg-line" :style="`bottom:${avgPct}%`"></div>
                  <div class="ff-avg-label" :style="`bottom:${avgPct}%`">avg {{ fmt(avgSpend) }}</div>
                  <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:14px;height:100%">
                    <div v-for="bar in chartBars" :key="bar.month" class="ff-bar-col">
                      <span class="ff-bar-val" :class="bar.current ? 'ff-bar-val--active' : ''">{{ bar.val }}</span>
                      <div class="ff-bar" :class="bar.current ? 'ff-bar--current' : ''" :style="`height:${bar.pct}%`"></div>
                      <span class="ff-bar-month" :class="bar.current ? 'ff-bar-month--active' : ''">{{ bar.month }}</span>
                    </div>
                  </div>
                </div>
                <div style="font:400 10px 'IBM Plex Sans';color:var(--text-3);text-align:right;margin-top:2px">* month in progress</div>

                <!-- Category breakdown -->
                <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
                  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:9px">
                    <div style="font:600 12px 'IBM Plex Sans';color:var(--text)">{{ currentMonthName }} spending by category</div>
                    <div style="font:600 12px 'IBM Plex Mono';color:var(--text-2)">{{ fmt(totalSpent) }}</div>
                  </div>
                  <div class="ff-category-bar">
                    <div v-for="cat in categories" :key="cat.label" :style="`width:${cat.pct}%;background:${cat.color}`"></div>
                  </div>
                  <div style="display:flex;flex-wrap:wrap;gap:7px 16px;margin-top:11px">
                    <div v-for="cat in categories" :key="cat.label" style="display:flex;align-items:center;gap:6px">
                      <span :style="`width:8px;height:8px;border-radius:2px;background:${cat.color}`"></span>
                      <span style="font:500 11.5px 'IBM Plex Sans';color:var(--text-2)">{{ cat.label }}</span>
                      <span style="font:500 11px 'IBM Plex Mono';color:var(--text-3)">{{ cat.amount }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Anomaly panel -->
              <div style="flex:1;min-width:280px;border-left:1px solid var(--border);padding-left:28px">
                <div style="display:flex;align-items:center;gap:7px">
                  <span class="material-symbols-outlined" style="font-size:18px;color:var(--bad)">warning</span>
                  <div style="font:600 13px 'IBM Plex Sans';color:var(--text)">Unusual transactions</div>
                </div>
                <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3);margin-top:3px;margin-bottom:6px">Flagged by the 2σ deviation rule</div>
                <div v-if="anomalies.length === 0" style="font:400 12px 'IBM Plex Sans';color:var(--text-3);padding:12px 0">
                  No anomalies detected this cycle.
                </div>
                <div v-for="tx in anomalies" :key="tx.name" style="display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--border)">
                  <div>
                    <div style="font:600 12.5px 'IBM Plex Sans';color:var(--text)">{{ tx.name }}</div>
                    <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3)">{{ tx.cat }} · {{ tx.date }}</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font:600 12.5px 'IBM Plex Mono';color:var(--text)">{{ tx.amount }}</div>
                    <div class="ff-sigma-badge ff-sigma--warn">+{{ tx.aboveAvg }} avg</div>
                  </div>
                </div>
                <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3);margin-top:12px">{{ anomalies.length }} transaction{{ anomalies.length !== 1 ? 's' : '' }} flagged this cycle.</div>
              </div>
            </div>
          </section>

          <!-- Widget 4: Budget Calendar (full width) -->
          <section class="ff-widget ff-widget--full">
            <div class="ff-widget-head">
              <div style="display:flex;align-items:center;gap:9px">
                <span class="material-symbols-outlined" style="font-size:20px;color:var(--text)">event</span>
                <span class="ff-widget-title">Prescriptive Budget Calendar</span>
              </div>
              <div style="font:400 12px 'IBM Plex Sans';color:var(--text-3)">{{ currentMonthName }}</div>
            </div>

            <div style="display:flex;gap:28px;flex-wrap:wrap">
              <!-- Calendar grid -->
              <div style="flex:1;min-width:380px">
                <div class="ff-cal-header">
                  <div v-for="d in ['SUN','MON','TUE','WED','THU','FRI','SAT']" :key="d" class="ff-cal-dow">{{ d }}</div>
                </div>
                <div class="ff-cal-grid">
                  <div
                    v-for="cell in calCells"
                    :key="cell.key"
                    class="ff-cal-cell"
                    :style="`background:${cell.cellBg};border:${cell.cellBorder}`"
                  >
                    <div v-if="!cell.blank" :style="`font:600 12px 'IBM Plex Mono';color:${cell.numColor}`">{{ cell.n }}</div>
                    <div v-if="cell.hasPlanned" class="ff-cal-event">
                      {{ cell.planned }} <span style="font-family:'IBM Plex Mono';color:var(--text)">{{ cell.plannedAmt }}</span>
                    </div>
                  </div>
                </div>
                <!-- Legend -->
                <div style="display:flex;flex-wrap:wrap;gap:14px;margin-top:14px">
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:var(--surface-2);border:1px solid var(--border-strong)"></span>
                    <span style="font:500 11px 'IBM Plex Sans';color:var(--text-2)">Planned expense</span>
                  </div>
                </div>
              </div>

              <!-- Spendable pool -->
              <div style="width:280px;flex-shrink:0;border-left:1px solid var(--border);padding-left:28px;display:flex;flex-direction:column">
                <div style="font:600 12px 'IBM Plex Sans';color:var(--text)">Remaining spendable pool</div>
                <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3);margin-top:2px;margin-bottom:14px">Cycle resets {{ nextMonthName }}</div>

                <div v-for="row in poolRows" :key="row.label" style="display:flex;justify-content:space-between;padding:7px 0;font:500 12.5px 'IBM Plex Sans';color:var(--text-2)">
                  {{ row.label }}
                  <span style="font-family:'IBM Plex Mono'" :style="`color:${row.color || 'var(--text)'}`">{{ row.val }}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:10px 0;margin-top:3px;border-top:1px dashed var(--border-strong);font:600 13px 'IBM Plex Sans';color:var(--text)">
                  Spendable pool<span style="font-family:'IBM Plex Mono'">{{ fmt(available) }}</span>
                </div>

                <div style="background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:14px;margin-top:8px;text-align:center">
                  <div style="font:500 11px 'IBM Plex Sans';color:var(--text-3)">{{ fmt(available) }} ÷ {{ daysRemaining }} days remaining</div>
                  <div style="margin-top:4px">
                    <span style="font:600 34px 'IBM Plex Mono';letter-spacing:-1px;color:var(--good)">{{ fmt(dailyBudget) }}</span>
                    <span style="font:500 13px 'IBM Plex Sans';color:var(--text-3)"> / day</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useUploadJobStore } from '@/stores/uploadJob'
import { useToastStore } from '@/stores/toast'

const store = useDashboardStore()
const router = useRouter()
const job = useUploadJobStore()
const toast = useToastStore()

const fileInput = ref(null)
const dragOver = ref(false)
const MAX_SIZE = 10 * 1024 * 1024

function validateFile(f) {
  if (f.type !== 'application/pdf' && !f.name.toLowerCase().endsWith('.csv')) {
    return 'Only PDF and CSV files are supported'
  }
  if (f.size > MAX_SIZE) return 'File must be under 10 MB'
  return null
}

// No bank selector on this widget (unlike the full /upload form) — default to
// "Unknown", same as the dedicated form's fallback option.
function startUpload(f) {
  const err = validateFile(f)
  if (err) {
    toast.push(err, 'error')
    return
  }
  job.upload(f, 'Unknown')
  router.push('/upload')
}

function onFile(e) {
  const f = e.target.files[0]
  if (f) startUpload(f)
}

function onDrop(e) {
  dragOver.value = false
  const f = e.dataTransfer.files[0]
  if (f) startUpload(f)
}
onMounted(() => store.load())

// ── Helpers ───────────────────────────────────────────────────
const fmt = n => '$' + Math.round(n).toLocaleString('en')
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const STK_COLORS = ['var(--stk1)','var(--stk2)','var(--stk3)','var(--stk4)','var(--stk5)','var(--stk6)','var(--stk7)']

// ── Stat strip ────────────────────────────────────────────────
const income = computed(() => store.budget?.breakdown.income ?? 0)
const spentThisCycle = computed(() => store.categories.total_spent ?? 0)
const dailyBudget = computed(() => store.budget?.daily_budget ?? 0)
const daysRemaining = computed(() => store.budget?.breakdown.days_remaining ?? 0)
const daysElapsed = computed(() => new Date().getDate())
const spentPct = computed(() => income.value ? Math.round(spentThisCycle.value / income.value * 100) : 0)
const available = computed(() => store.budget?.breakdown.available ?? 0)

// ── Health score (live from store, loads after main data) ─────
const C = 439.823
const scoreOffset = computed(() => {
  const s = store.healthScore?.score
  return s != null ? (C * (1 - s / 100)).toFixed(1) : C
})
const scoreColor = computed(() => {
  const s = store.healthScore?.score
  if (s == null) return 'var(--text-3)'
  return s >= 65 ? 'var(--good)' : s >= 50 ? 'var(--warn)' : 'var(--bad)'
})
const scoreLabel = computed(() => {
  const s = store.healthScore?.score
  if (s == null) return ''
  return s >= 80 ? 'Strong' : s >= 65 ? 'Good' : s >= 50 ? 'Fair' : 'At risk'
})
const dimensions = computed(() => {
  if (!store.healthScore) return []
  const { dimensions: dims, weakest_dimension } = store.healthScore
  return Object.entries(dims).map(([key, d]) => ({
    label: d.label,
    score: d.score,
    max: d.max,
    pct: Math.round(d.score / d.max * 100),
    color: key === weakest_dimension ? 'var(--warn)' : 'var(--good)',
    weakest: key === weakest_dimension,
  }))
})

// ── Analytics: bar chart ──────────────────────────────────────
const chartBars = computed(() => {
  if (!store.monthlyTrend.length) return []
  const maxVal = Math.max(...store.monthlyTrend.map(p => p.total), 1)
  const now = new Date()
  return store.monthlyTrend.map(p => {
    const [yr, mo] = p.date.split('-')
    const isCurrent = +yr === now.getFullYear() && +mo - 1 === now.getMonth()
    const month = new Date(+yr, +mo - 1, 1).toLocaleString('en', { month: 'short' })
    const val = Math.round(p.total).toLocaleString('en')
    return { month, val: isCurrent ? `${val}*` : val, pct: Math.round(p.total / maxVal * 100), current: isCurrent }
  })
})

const avgSpend = computed(() => {
  if (!store.monthlyTrend.length) return 0
  return store.monthlyTrend.reduce((s, p) => s + p.total, 0) / store.monthlyTrend.length
})

const avgPct = computed(() => {
  if (!store.monthlyTrend.length) return 0
  const maxVal = Math.max(...store.monthlyTrend.map(p => p.total), 1)
  return Math.round(avgSpend.value / maxVal * 100)
})

// ── Analytics: categories ─────────────────────────────────────
const categories = computed(() =>
  (store.categories.categories ?? []).map((c, i) => ({
    label: c.category,
    amount: fmt(c.total),
    pct: c.percentage,
    color: STK_COLORS[i % STK_COLORS.length],
  }))
)

const totalSpent = computed(() => store.categories.total_spent ?? 0)

const currentMonthName = computed(() => {
  const now = new Date()
  return `${MONTHS[now.getMonth()]} ${now.getFullYear()}`
})

// ── Analytics: anomalies ──────────────────────────────────────
// Backend returns amount_above (withdrawal - category mean), not sigma value
const anomalies = computed(() =>
  (store.anomalies ?? []).slice(0, 5).map(a => {
    const [, mo, day] = a.date.split('-')
    return {
      name: a.description,
      cat: a.category,
      date: `${+day} ${MONTHS[+mo - 1]}`,
      amount: `$${(+a.withdrawal).toFixed(2)}`,
      aboveAvg: `$${(+a.amount_above).toFixed(2)}`,
    }
  })
)

// ── Budget calendar ───────────────────────────────────────────
const calCells = computed(() => {
  const now = new Date()
  const firstDayOfWeek = new Date(now.getFullYear(), now.getMonth(), 1).getDay()
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
  const today = now.getDate()

  const plannedMap = {}
  for (const e of (store.upcoming ?? [])) {
    const day = +e.due_date.split('-')[2]
    plannedMap[day] = [e.name, fmt(e.amount)]
  }

  const cells = Array.from({ length: firstDayOfWeek }, (_, i) => (
    { key: `blank${i}`, blank: true, cellBg: 'transparent', cellBorder: '1px solid transparent' }
  ))
  for (let n = 1; n <= daysInMonth; n++) {
    const isToday = n === today
    const p = plannedMap[n]
    cells.push({
      key: 'd' + n, blank: false, n,
      cellBg: isToday ? 'var(--brand)' : 'var(--surface)',
      cellBorder: isToday ? '1px solid var(--brand)' : '1px solid var(--border)',
      numColor: isToday ? 'var(--on-brand)' : 'var(--text-2)',
      hasPlanned: !!p, planned: p?.[0] ?? '', plannedAmt: p?.[1] ?? '',
    })
  }
  return cells
})

// ── Spendable pool ────────────────────────────────────────────
const poolRows = computed(() => {
  const b = store.budget?.breakdown
  if (!b) return []
  return [
    { label: 'Income',           val: `+${Math.round(b.income).toLocaleString('en')}`,           color: 'var(--good)' },
    { label: 'Fixed bills',      val: `−${Math.round(b.fixed_bills).toLocaleString('en')}` },
    { label: 'Planned expenses', val: `−${Math.round(b.planned_expenses).toLocaleString('en')}` },
  ]
})

const nextMonthName = computed(() => {
  const now = new Date()
  return `1 ${MONTHS[(now.getMonth() + 1) % 12]}`
})
</script>

<style scoped>
.ff-app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}
.ff-page-content {
  padding: 22px 28px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Stat strip ── */
.ff-stat-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
.ff-stat-cell {
  background: var(--surface);
  padding: 16px 20px;
}
.ff-stat-label {
  font: 600 10.5px 'IBM Plex Sans';
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--text-3);
}
.ff-stat-value {
  font: 600 23px 'IBM Plex Mono';
  color: var(--text);
  margin-top: 7px;
  letter-spacing: -.5px;
}
.ff-stat-meta {
  margin-top: 5px;
  font: 500 11.5px 'IBM Plex Sans';
  color: var(--text-3);
}

/* ── Widget grid ── */
.ff-widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
  gap: 20px;
  align-items: start;
}
.ff-widget {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 22px;
}
.ff-widget--full { grid-column: 1 / -1; }
.ff-widget-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.ff-widget-title {
  font: 600 14.5px 'IBM Plex Sans';
  color: var(--text);
}

/* Upload widget */
.ff-drop-zone {
  border: 1.5px dashed var(--border-strong);
  border-radius: 8px;
  background: var(--surface-2);
  padding: 24px 20px;
  text-align: center;
  display: block;
  text-decoration: none;
  cursor: pointer;
  transition: border-color 150ms ease-out, background 150ms ease-out;
}
.ff-drop-zone-active {
  border-color: var(--brand);
  background: color-mix(in srgb, var(--brand) 8%, var(--surface-2));
}
.ff-bank-tag {
  font: 600 11px 'IBM Plex Mono';
  color: var(--text-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 11px;
  background: var(--surface);
}
.ff-progress-track {
  height: 6px;
  border-radius: 3px;
  background: var(--surface-2);
  overflow: hidden;
}
.ff-progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 600ms ease;
}

/* Health score */
.ff-score-label {
  margin-top: 7px;
  font: 600 10.5px 'IBM Plex Sans';
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 10px;
}
.ff-weakest-badge {
  font: 600 9px 'IBM Plex Sans';
  color: var(--warn);
  background: var(--warn-bg);
  border: 1px solid var(--warn-bd);
  border-radius: 4px;
  padding: 1px 5px;
  text-transform: uppercase;
  letter-spacing: .03em;
}
.ff-insight-box {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 13px;
  display: flex;
  gap: 11px;
}

/* Analytics */
.ff-avg-line {
  position: absolute;
  left: 0; right: 0;
  border-top: 1px dashed var(--border-strong);
}
.ff-avg-label {
  position: absolute;
  right: 0;
  transform: translateY(-100%);
  font: 500 10px 'IBM Plex Mono';
  color: var(--text-3);
  background: var(--surface);
  padding: 0 4px;
}
.ff-bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  gap: 6px;
}
.ff-bar-val {
  font: 500 10px 'IBM Plex Mono';
  color: var(--text-3);
}
.ff-bar-val--active { font-weight: 600; color: var(--text-2); }
.ff-bar {
  width: 100%;
  max-width: 44px;
  background: var(--chart-bar);
  border-radius: 5px 5px 0 0;
}
.ff-bar--current {
  background: repeating-linear-gradient(45deg, var(--surface-2), var(--surface-2) 4px, var(--surface-3) 4px, var(--surface-3) 8px);
  border: 1px solid var(--border-strong);
  border-bottom: none;
}
.ff-bar-month {
  font: 500 11px 'IBM Plex Sans';
  color: var(--text-3);
}
.ff-bar-month--active { font-weight: 600; color: var(--text); }
.ff-category-bar {
  display: flex;
  height: 12px;
  border-radius: 6px;
  overflow: hidden;
}
.ff-sigma-badge {
  font: 600 10px 'IBM Plex Mono';
  border-radius: 4px;
  padding: 1px 5px;
  margin-top: 3px;
  display: inline-block;
}
.ff-sigma--warn { color: var(--warn); background: var(--warn-bg); border: 1px solid var(--warn-bd); }

/* Calendar */
.ff-cal-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
  margin-bottom: 6px;
}
.ff-cal-dow {
  font: 600 10.5px 'IBM Plex Sans';
  color: var(--text-3);
  text-align: center;
}
.ff-cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}
.ff-cal-cell {
  min-height: 64px;
  border-radius: 6px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.ff-cal-event {
  font: 500 9px 'IBM Plex Sans';
  color: var(--text-2);
  background: var(--surface-2);
  border-radius: 3px;
  padding: 2px 4px;
  line-height: 1.25;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
