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
            <div class="ff-stat-value">$5,200</div>
            <div class="ff-badge ff-badge--good">
              <span class="material-symbols-outlined" style="font-size:15px">arrow_upward</span>3.2% vs May
            </div>
          </div>
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Spent this cycle</div>
            <div class="ff-stat-value">$3,260</div>
            <div class="ff-stat-meta">62% of income · 18 days</div>
          </div>
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Safe daily budget</div>
            <div class="ff-stat-value" style="color:var(--good)">$162</div>
            <div class="ff-stat-meta">12 days remaining</div>
          </div>
          <div class="ff-stat-cell">
            <div class="ff-stat-label">Health score</div>
            <div class="ff-stat-value">{{ score }}<span style="font-size:14px;color:var(--text-3)">/100</span></div>
            <div class="ff-badge ff-badge--good">
              <span class="material-symbols-outlined" style="font-size:15px">arrow_upward</span>4 pts vs May
            </div>
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
              <div style="display:flex;align-items:center;gap:10px">
                <div class="ff-live-badge">
                  <span class="ff-live-dot"></span>Parsing
                </div>
              </div>
            </div>

            <!-- Drop zone -->
            <router-link to="/upload" class="ff-drop-zone">
              <span class="material-symbols-outlined" style="font-size:30px;color:var(--text-3)">file_upload</span>
              <div style="font:600 13.5px 'IBM Plex Sans';color:var(--text);margin-top:8px">Drop a statement, or <span style="text-decoration:underline;text-underline-offset:2px">browse files</span></div>
              <div style="font:400 11.5px 'IBM Plex Sans';color:var(--text-3);margin-top:4px">PDF or CSV · up to 10 MB</div>
              <div style="display:flex;justify-content:center;gap:7px;margin-top:13px">
                <span class="ff-bank-tag">DBS</span>
                <span class="ff-bank-tag">OCBC</span>
                <span class="ff-bank-tag">UOB</span>
              </div>
            </router-link>

            <!-- Parsing progress -->
            <div class="ff-parse-card">
              <div style="display:flex;align-items:center;gap:11px">
                <div style="width:34px;height:34px;border-radius:7px;background:var(--bad-bg);display:flex;align-items:center;justify-content:center;flex-shrink:0">
                  <span class="material-symbols-outlined" style="font-size:19px;color:var(--bad)">picture_as_pdf</span>
                </div>
                <div style="flex:1;min-width:0">
                  <div style="font:600 13px 'IBM Plex Sans';color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">DBS_eStatement_May2026.pdf</div>
                  <div style="font:400 11px 'IBM Plex Mono';color:var(--text-3)">1.2 MB · 142 transactions</div>
                </div>
                <div style="font:600 13px 'IBM Plex Mono';color:var(--good)">{{ parsingPct }}%</div>
              </div>
              <div class="ff-progress-track" style="margin-top:11px">
                <div class="ff-progress-bar" :style="`width:${parsingPct}%`"></div>
              </div>
              <!-- Steps -->
              <div style="display:flex;justify-content:space-between;margin-top:14px">
                <div class="ff-step" v-for="step in parseSteps" :key="step.label">
                  <div class="ff-step-dot" :class="step.state">
                    <span v-if="step.state === 'done'" class="material-symbols-outlined" style="font-size:15px;color:var(--surface)">check</span>
                    <span v-else-if="step.state === 'active'" class="ff-step-inner-dot"></span>
                    <span v-else style="font:600 11px 'IBM Plex Mono';color:var(--text-3)">{{ step.num }}</span>
                  </div>
                  <div class="ff-step-label" :class="step.state === 'active' ? 'ff-step-label--active' : ''">{{ step.label }}</div>
                </div>
              </div>
              <div style="display:flex;align-items:center;justify-content:space-between;margin-top:13px;padding-top:11px;border-top:1px solid var(--border)">
                <div style="font:500 11px 'IBM Plex Sans';color:var(--text-2)">Categorising row 97 of 142…</div>
                <div style="font:500 10px 'IBM Plex Mono';color:var(--text-3)">pdfplumber + anthropic</div>
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
              <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3)">Updated 1 Jun</div>
            </div>

            <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center">
              <!-- Gauge -->
              <div style="position:relative;width:164px;height:164px;flex-shrink:0;margin:0 auto">
                <svg width="164" height="164" style="transform:rotate(-90deg)">
                  <circle cx="82" cy="82" r="70" fill="none" style="stroke:var(--surface-2)" stroke-width="13"/>
                  <circle cx="82" cy="82" r="70" fill="none" :style="`stroke:${scoreColor}`" stroke-width="13" stroke-linecap="round" stroke-dasharray="439.8" :stroke-dashoffset="scoreOffset"/>
                </svg>
                <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">
                  <div style="font:600 42px 'IBM Plex Mono';letter-spacing:-1.5px;line-height:1;color:var(--text)">{{ score }}</div>
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
                    <span style="font:600 12.5px 'IBM Plex Mono';color:var(--text)">{{ dim.val }}</span>
                  </div>
                  <div class="ff-progress-track">
                    <div class="ff-progress-bar" :style="`width:${dim.val}%;background:${dim.color}`"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI insight -->
            <div class="ff-insight-box" style="margin-top:18px">
              <span class="material-symbols-outlined" style="font-size:19px;color:var(--brand);flex-shrink:0">auto_awesome</span>
              <div>
                <div style="font:600 10px 'IBM Plex Sans';letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);margin-bottom:3px">AI insight · weakest dimension</div>
                <div style="font:400 12.5px/1.5 'IBM Plex Sans';color:var(--text-2)">Your discretionary spend swings ±$210 week to week. Capping dining &amp; shopping at <strong style="color:var(--text)">$200/week</strong> would steady cash flow and lift your score by an estimated 6 points.</div>
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
              <div style="display:flex;align-items:center;gap:12px">
                <div class="ff-range-tabs">
                  <span class="ff-range-tab ff-range-tab--active">6M</span>
                  <span class="ff-range-tab">1Y</span>
                  <span class="ff-range-tab">All</span>
                </div>
              </div>
            </div>

            <div style="display:flex;gap:28px;flex-wrap:wrap">
              <!-- Bar chart + category breakdown -->
              <div style="flex:2;min-width:340px">
                <div style="position:relative;height:200px;padding-top:18px">
                  <div class="ff-avg-line"></div>
                  <div class="ff-avg-label">avg $3,250</div>
                  <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:14px;height:100%">
                    <div v-for="bar in chartBars" :key="bar.month" class="ff-bar-col">
                      <span class="ff-bar-val" :class="bar.current ? 'ff-bar-val--active' : ''">{{ bar.val }}</span>
                      <div class="ff-bar" :class="bar.current ? 'ff-bar--current' : ''" :style="`height:${bar.pct}%`"></div>
                      <span class="ff-bar-month" :class="bar.current ? 'ff-bar-month--active' : ''">{{ bar.month }}</span>
                    </div>
                  </div>
                </div>
                <div style="font:400 10px 'IBM Plex Sans';color:var(--text-3);text-align:right;margin-top:2px">* June in progress</div>

                <!-- Category breakdown -->
                <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
                  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:9px">
                    <div style="font:600 12px 'IBM Plex Sans';color:var(--text)">May spending by category</div>
                    <div style="font:600 12px 'IBM Plex Mono';color:var(--text-2)">$3,210</div>
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
                <div v-for="tx in anomalies" :key="tx.name" style="display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--border)">
                  <div>
                    <div style="font:600 12.5px 'IBM Plex Sans';color:var(--text)">{{ tx.name }}</div>
                    <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3)">{{ tx.cat }} · {{ tx.date }}</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font:600 12.5px 'IBM Plex Mono';color:var(--text)">{{ tx.amount }}</div>
                    <div class="ff-sigma-badge" :class="tx.level === 'bad' ? 'ff-sigma--bad' : 'ff-sigma--warn'">{{ tx.sigma }}</div>
                  </div>
                </div>
                <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3);margin-top:12px">3 of 142 transactions flagged this cycle.</div>
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
              <div style="font:400 12px 'IBM Plex Sans';color:var(--text-3)">June 2026</div>
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
                    <div v-if="cell.hasStatus" class="ff-cal-status" :style="`background:${cell.statusColor}`"></div>
                  </div>
                </div>
                <!-- Legend -->
                <div style="display:flex;flex-wrap:wrap;gap:14px;margin-top:14px">
                  <div v-for="lg in calLegend" :key="lg.label" style="display:flex;align-items:center;gap:6px">
                    <span :style="lg.style"></span>
                    <span style="font:500 11px 'IBM Plex Sans';color:var(--text-2)">{{ lg.label }}</span>
                  </div>
                </div>
              </div>

              <!-- Spendable pool -->
              <div style="width:280px;flex-shrink:0;border-left:1px solid var(--border);padding-left:28px;display:flex;flex-direction:column">
                <div style="font:600 12px 'IBM Plex Sans';color:var(--text)">Remaining spendable pool</div>
                <div style="font:400 11px 'IBM Plex Sans';color:var(--text-3);margin-top:2px;margin-bottom:14px">Cycle resets 1 Jul</div>

                <div v-for="row in poolRows" :key="row.label" style="display:flex;justify-content:space-between;padding:7px 0;font:500 12.5px 'IBM Plex Sans';color:var(--text-2)">
                  {{ row.label }}
                  <span style="font-family:'IBM Plex Mono'" :style="`color:${row.color || 'var(--text)'}`">{{ row.val }}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:10px 0;margin-top:3px;border-top:1px dashed var(--border-strong);font:600 13px 'IBM Plex Sans';color:var(--text)">
                  Spendable pool<span style="font-family:'IBM Plex Mono'">$1,940</span>
                </div>

                <div style="background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:14px;margin-top:8px;text-align:center">
                  <div style="font:500 11px 'IBM Plex Sans';color:var(--text-3)">$1,940 ÷ 12 days remaining</div>
                  <div style="margin-top:4px">
                    <span style="font:600 34px 'IBM Plex Mono';letter-spacing:-1px;color:var(--good)">$162</span>
                    <span style="font:500 13px 'IBM Plex Sans';color:var(--text-3)"> / day</span>
                  </div>
                  <div class="ff-on-track">
                    <span class="material-symbols-outlined" style="font-size:15px">check_circle</span>On track
                  </div>
                </div>
                <div style="font:400 11px/1.5 'IBM Plex Sans';color:var(--text-3);margin-top:12px">Safe daily spend to hit your $800 savings goal and cover all planned costs.</div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

// ── Health score ──────────────────────────────────────────────
// ponytail: static demo value; wire to health_scores store when API is ready
const score = 78
const C = 439.823
const scoreOffset = computed(() => (C * (1 - score / 100)).toFixed(1))
const scoreColor = computed(() => score >= 65 ? 'var(--good)' : score >= 50 ? 'var(--warn)' : 'var(--bad)')
const scoreLabel = computed(() => score >= 80 ? 'Strong' : score >= 65 ? 'Good' : score >= 50 ? 'Fair' : 'At risk')

const dimensions = [
  { label: 'Savings rate',       val: 82, color: 'var(--good)' },
  { label: 'Expense volatility', val: 58, color: 'var(--warn)', weakest: true },
  { label: 'Bill regularity',    val: 91, color: 'var(--good)' },
  { label: 'Budget adherence',   val: 73, color: 'var(--good)' },
]

// ── Parsing widget ────────────────────────────────────────────
// ponytail: static demo; wire to upload store progress when real upload is wired
const parsingPct = 68
const parseSteps = [
  { label: 'Uploaded',       state: 'done',    num: '1' },
  { label: 'Extract tables', state: 'done',    num: '2' },
  { label: 'Claude parsing', state: 'active',  num: '3' },
  { label: 'Ledger write',   state: 'pending', num: '4' },
]

// ── Analytics ─────────────────────────────────────────────────
const chartBars = [
  { month: 'Jan', val: '3,120', pct: 78 },
  { month: 'Feb', val: '2,980', pct: 74 },
  { month: 'Mar', val: '3,340', pct: 83 },
  { month: 'Apr', val: '3,580', pct: 89 },
  { month: 'May', val: '3,210', pct: 80 },
  { month: 'Jun', val: '1,980*', pct: 49, current: true },
]

const categories = [
  { label: 'Food & Dining', amount: '$880',  pct: 27.4, color: 'var(--stk1)' },
  { label: 'Groceries',     amount: '$520',  pct: 16.2, color: 'var(--stk2)' },
  { label: 'Shopping',      amount: '$560',  pct: 17.4, color: 'var(--stk3)' },
  { label: 'Transport',     amount: '$410',  pct: 12.8, color: 'var(--stk4)' },
  { label: 'Utilities',     amount: '$410',  pct: 12.8, color: 'var(--stk5)' },
  { label: 'Healthcare',    amount: '$245',  pct:  7.6, color: 'var(--stk6)' },
  { label: 'Others',        amount: '$185',  pct:  5.8, color: 'var(--stk7)' },
]

const anomalies = [
  { name: 'ParkwayHealth', cat: 'Healthcare', date: '12 Jun', amount: '$245.00', sigma: '2.4σ', level: 'bad' },
  { name: 'Shopee',        cat: 'Shopping',   date: '09 Jun', amount: '$389.00', sigma: '2.1σ', level: 'warn' },
  { name: 'Grab',          cat: 'Transport',  date: '05 Jun', amount: '$112.40', sigma: '2.6σ', level: 'bad' },
]

// ── Budget calendar ───────────────────────────────────────────
const calCells = computed(() => {
  const statusMap = { 1:'g',2:'g',3:'w',4:'o',5:'g',6:'g',7:'w',8:'g',9:'g',10:'w',11:'o',12:'g',13:'g',14:'o',15:'g',16:'g',17:'w',18:'o' }
  const plannedMap = { 24:['Insurance','$180'], 27:['Concert','$260'], 30:['Phone','$65'] }
  const colorMap = { g: 'var(--good)', w: 'var(--warn)', o: 'var(--bad)' }
  const today = new Date().getDate()

  const cells = [{ key: 'blank', blank: true, cellBg: 'transparent', cellBorder: '1px solid transparent' }]
  for (let n = 1; n <= 30; n++) {
    const isToday = n === today
    const s = statusMap[n]
    const p = plannedMap[n]
    cells.push({
      key: 'd' + n, blank: false, n,
      cellBg: isToday ? 'var(--brand)' : 'var(--surface)',
      cellBorder: isToday ? '1px solid var(--brand)' : '1px solid var(--border)',
      numColor: isToday ? 'var(--on-brand)' : 'var(--text-2)',
      hasStatus: !!s, statusColor: s ? colorMap[s] : 'transparent',
      hasPlanned: !!p, planned: p?.[0] ?? '', plannedAmt: p?.[1] ?? '',
    })
  }
  return cells
})

const calLegend = [
  { label: 'Under budget', style: 'display:inline-block;width:14px;height:4px;border-radius:2px;background:var(--good)' },
  { label: 'Near limit',   style: 'display:inline-block;width:14px;height:4px;border-radius:2px;background:var(--warn)' },
  { label: 'Over budget',  style: 'display:inline-block;width:14px;height:4px;border-radius:2px;background:var(--bad)' },
  { label: 'Planned expense', style: 'display:inline-block;width:9px;height:9px;border-radius:2px;background:var(--surface-2);border:1px solid var(--border-strong)' },
]

const poolRows = [
  { label: 'Income',            val: '+5,200', color: 'var(--good)' },
  { label: 'Fixed bills',       val: '−1,840' },
  { label: 'Planned expenses',  val: '−620' },
  { label: 'Savings goal',      val: '−800' },
]
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
.ff-badge {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-top: 5px;
  font: 500 11.5px 'IBM Plex Sans';
}
.ff-badge--good { color: var(--good); }

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
.ff-live-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font: 600 11px 'IBM Plex Sans';
  color: var(--good);
  background: var(--good-bg);
  border: 1px solid var(--good-bd);
  border-radius: 999px;
  padding: 3px 9px;
}
.ff-live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--good);
  animation: finflowPulse 1.4s ease-in-out infinite;
}
.ff-drop-zone {
  border: 1.5px dashed var(--border-strong);
  border-radius: 8px;
  background: var(--surface-2);
  padding: 24px 20px;
  text-align: center;
  display: block;
  text-decoration: none;
  cursor: pointer;
}
.ff-bank-tag {
  font: 600 11px 'IBM Plex Mono';
  color: var(--text-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 11px;
  background: var(--surface);
}
.ff-parse-card {
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
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
  background: linear-gradient(90deg, var(--brand), var(--sage), var(--brand));
  background-size: 200px 100%;
  animation: finflowShimmer 1.1s linear infinite;
}
.ff-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  flex: 1;
}
.ff-step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ff-step-dot.done   { background: var(--good); }
.ff-step-dot.active { border: 2px solid var(--good); animation: finflowPulse 1.3s ease-in-out infinite; }
.ff-step-dot.pending { background: var(--surface-2); }
.ff-step-inner-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--good);
}
.ff-step-label {
  font: 500 9.5px 'IBM Plex Sans';
  color: var(--text-3);
  text-align: center;
}
.ff-step-label--active {
  font-weight: 600;
  color: var(--text);
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
.ff-range-tabs {
  display: flex;
  gap: 2px;
  background: var(--surface-2);
  border-radius: 7px;
  padding: 3px;
}
.ff-range-tab {
  font: 500 11.5px 'IBM Plex Sans';
  color: var(--text-3);
  padding: 5px 12px;
  cursor: pointer;
  border-radius: 5px;
}
.ff-range-tab--active {
  font-weight: 600;
  color: var(--text);
  background: var(--surface);
}
.ff-avg-line {
  position: absolute;
  left: 0; right: 0;
  bottom: 79%;
  border-top: 1px dashed var(--border-strong);
}
.ff-avg-label {
  position: absolute;
  right: 0;
  bottom: 79%;
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
.ff-sigma--bad  { color: var(--bad);  background: var(--bad-bg);  border: 1px solid var(--bad-bd); }
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
.ff-cal-status {
  height: 4px;
  border-radius: 2px;
}
.ff-on-track {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  font: 600 11px 'IBM Plex Sans';
  color: var(--good);
  background: var(--good-bg);
  border: 1px solid var(--good-bd);
  border-radius: 999px;
  padding: 3px 10px;
}
</style>
