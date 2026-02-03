<template>
  <div class="card">
    <div class="row spread mb12">
      <div>
        <h3 class="h3">Detalhe da operadora</h3>
        <p class="muted small">Informações cadastrais e histórico de despesas.</p>
      </div>

      <RouterLink class="btn secondary" to="/operadoras">← Voltar</RouterLink>
    </div>

    <Loading v-if="loading" />
    <ErrorBox v-else-if="error" :message="error" />

    <div v-else>
      <div class="grid two">
        <div class="card">
          <h4 class="h4">Dados cadastrais</h4>

          <p><span class="muted">Razão Social:</span><br /><strong>{{ operadora.razao_social }}</strong></p>
          <p><span class="muted">CNPJ:</span><br /><strong>{{ operadora.cnpj }}</strong></p>

          <div class="row spread">
            <p><span class="muted">UF:</span><br /><strong>{{ operadora.uf || "-" }}</strong></p>
            <p><span class="muted">Registro ANS:</span><br /><strong>{{ operadora.registro_ans ?? "-" }}</strong></p>
          </div>
        </div>

        <div class="card">
          <h4 class="h4">Histórico de despesas</h4>
          <p class="muted small">Valores por ano/trimestre.</p>

          <p v-if="despesas.length === 0" class="muted">Sem despesas registradas para esta operadora.</p>
          <div v-else style="height: 320px;">
            <canvas ref="lineCanvas"></canvas>
          </div>

        </div>
      </div>

      <div class="card mt16" v-if="despesas.length > 0">
        <h4 class="h4">Tabela de despesas</h4>

        <table class="table">
          <thead>
            <tr>
              <th style="width:120px;">Período</th>
              <th style="width:220px;">Valor</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in despesas" :key="`${d.ano}-${d.trimestre}`">
              <td>{{ d.ano }}T{{ d.trimestre }}</td>
              <td>{{ formatBR(d.valor_despesas) }}</td>
            </tr>
          </tbody>
        </table>
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

const props = defineProps({ cnpj: { type: String, required: true } });

const loading = ref(true);
const error = ref("");

const operadora = ref(null);
const despesas = ref([]);

const lineCanvas = ref(null);
let chartInstance = null;

function formatBR(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

async function loadAll() {
  loading.value = true;
  error.value = "";

  try {
    const [opRes, despRes] = await Promise.all([
      api.get(`/api/operadoras/${props.cnpj}`),
      api.get(`/api/operadoras/${props.cnpj}/despesas`),
    ]);

    operadora.value = opRes.data;
    despesas.value = despRes.data;

    loading.value = false;
    await nextTick();

    if (despesas.value.length > 0 && lineCanvas.value) {
      const ctx = lineCanvas.value.getContext("2d");
      if (!ctx) return;

      const labels = despesas.value.map((d) => `${d.ano}T${d.trimestre}`);
      const values = despesas.value.map((d) => Number(d.valor_despesas));

      if (chartInstance) chartInstance.destroy();

      chartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [{ label: "Despesas", data: values }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,

            animation: {
                duration: 1200,
                easing: "easeOutQuart",
                delay: (ctx) => (ctx.type === "data" ? ctx.dataIndex * 120 : 0),
            },

            // força a linha "subir do zero"
            animations: {
                y: {
                from: 0,
                duration: 1200,
                easing: "easeOutQuart",
                },
            },

            elements: {
                line: { tension: 0.25 }, // suaviza levemente
                point: { radius: 3 },
            },

            plugins: {
                tooltip: {
                callbacks: {
                    label: (c) => `${c.dataset.label}: ${formatBR(c.raw)}`,
                },
                },
            },
        }
      });
    }
  } catch (e) {
    console.error(e);
    const status = e?.response?.status;
    if (status === 404) error.value = "Operadora não encontrada.";
    else error.value = status ? `Falha ao carregar detalhes (HTTP ${status}).` : "Falha ao carregar detalhes.";
    loading.value = false;
  }
}

onMounted(loadAll);
</script>