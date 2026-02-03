<template>
  <div class="card">
    <h3 class="h3">Dashboard</h3>
    <p class="muted small">Visão geral de despesas e distribuição por UF.</p>

    <Loading v-if="loading" />
    <ErrorBox v-else-if="error" :message="error" />

    <div v-else>
      <div class="kpi mt12">
        <div class="box">
          <div class="label">Total despesas</div>
          <div class="value">{{ formatBR(stats.total_despesas) }}</div>
        </div>
        <div class="box">
          <div class="label">Média</div>
          <div class="value">{{ formatBR(stats.media_despesas) }}</div>
        </div>
      </div>

      <div class="grid two mt16">
        <div class="card">
            <h4 class="h4">Distribuição por UF</h4>
            <p class="muted small">Totais agregados por unidade federativa.</p>
            <div class="row mb12">
            <label class="muted small">Top UFs</label>
            <select class="select" v-model.number="ufTop" @change="renderChart()">
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="27">Todas</option>
            </select>

            <button class="btn secondary" @click="loadStats()">Atualizar</button>
            </div>

          <div style="height: 320px;">
            <canvas v-if="stats" ref="ufCanvas"></canvas>
          </div>

        </div>

        <div class="card">
          <h4 class="h4">Top 5 operadoras</h4>
          <p class="muted small">Ranking por total de despesas no período.</p>
          <ol>
            <li v-for="o in stats.top5_operadoras" :key="o.cnpj">
              <strong>{{ o.razao_social }}</strong>
              <span class="muted"> — {{ formatBR(o.total) }}</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from "vue";
import { api } from "../api/client";
import Loading from "../components/Loading.vue";
import ErrorBox from "../components/ErrorBox.vue";
import { Chart } from "chart.js/auto";

const ufTop = ref(10);
const refreshKey = ref(0);

const loading = ref(true);
const error = ref("");
const stats = ref(null);

const ufCanvas = ref(null);
let chartInstance = null;

function formatBR(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function renderChart() {
  if (!stats.value || !ufCanvas.value) return;

  const ctx = ufCanvas.value.getContext("2d");
  if (!ctx) return;

  const list = [...stats.value.despesas_por_uf]
    .sort((a, b) => Number(b.total) - Number(a.total))
    .slice(0, ufTop.value);

  const labels = list.map((x) => x.uf);
  const values = list.map((x) => Number(x.total));

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Total de despesas", data: values }],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,

        // força animações (e evita "pular" por alguma config externa)
        animation: {
            duration: 1200,
            easing: "easeOutQuart",
            delay: (ctx) => (ctx.type === "data" ? ctx.dataIndex * 80 : 0),
        },
        animations: {
            y: {
            from: 0, // começa do zero
            duration: 1200,
            easing: "easeOutQuart",
            },
        },

        plugins: {
            tooltip: {
            callbacks: {
                label: (c) => `Total: ${formatBR(c.raw)}`,
            },
            },
        },
    }
  });
}


async function loadStats() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/api/estatisticas");
    stats.value = data;

    // libera renderização e garante o canvas no DOM
    loading.value = false;
    await nextTick();
    renderChart();

  } catch (e) {
    console.error(e);
    const status = e?.response?.status;
    const detail = e?.response?.data?.detail;
    error.value = status
      ? `Falha ao carregar estatísticas (HTTP ${status})${detail ? ` - ${detail}` : ""}`
      : "Falha ao carregar estatísticas (sem resposta do servidor).";
    loading.value = false;
  }
}
onMounted(loadStats);
</script>