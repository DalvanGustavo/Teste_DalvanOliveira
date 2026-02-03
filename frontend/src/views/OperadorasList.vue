<template>
  <div class="card">
    <div class="row spread mb12">
      <div>
        <h3 class="h3">Operadoras</h3>
        <p class="muted small">Tabela paginada com busca por CNPJ ou Razão Social.</p>
      </div>

      <div class="muted small">
        Total: <strong>{{ total }}</strong>
      </div>
    </div>

    <div class="row mb12">
      <input
        v-model="search"
        class="input"
        placeholder="Buscar por Razão Social ou CNPJ"
        @keyup.enter="applySearch"
      />
      <button class="btn" @click="applySearch">Buscar</button>
      <button class="btn secondary" @click="clearSearch" :disabled="!search && !appliedSearch">
        Limpar
      </button>
    </div>

    <Loading v-if="loading" />
    <ErrorBox v-else-if="error" :message="error" />

    <div v-else>
      <p v-if="total === 0" class="muted">Nenhuma operadora encontrada.</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th style="width: 170px;">CNPJ</th>
            <th>Razão Social</th>
            <th style="width: 70px;">UF</th>
            <th style="width: 90px;"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in rows" :key="o.cnpj">
            <td>{{ o.cnpj }}</td>
            <td>{{ o.razao_social }}</td>
            <td>{{ o.uf || "-" }}</td>
            <td>
              <RouterLink :to="`/operadoras/${o.cnpj}`">Detalhes</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="row spread mt12">
        <div class="muted">
          Página <strong>{{ page }}</strong> de <strong>{{ totalPages }}</strong>
        </div>

        <div class="row gap8">
          <button class="btn secondary" @click="prev" :disabled="page <= 1">Anterior</button>
          <button class="btn secondary" @click="next" :disabled="page >= totalPages">Próxima</button>

          <select class="select" v-model.number="limit" @change="changeLimit">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../api/client";
import Loading from "../components/Loading.vue";
import ErrorBox from "../components/ErrorBox.vue";

const loading = ref(true);
const error = ref("");

const rows = ref([]);
const total = ref(0);

const page = ref(1);
const limit = ref(10);

const search = ref("");
const appliedSearch = ref("");

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit.value)));

async function fetchData() {
  loading.value = true;
  error.value = "";

  try {
    const params = { page: page.value, limit: limit.value };
    if (appliedSearch.value) params.search = appliedSearch.value;

    const { data } = await api.get("/api/operadoras", { params });
    rows.value = data.data;
    total.value = data.total;
  } catch (e) {
    console.error(e);
    const status = e?.response?.status;
    error.value = status
      ? `Falha ao carregar operadoras (HTTP ${status}).`
      : "Falha ao carregar operadoras (sem resposta do servidor).";
  } finally {
    loading.value = false;
  }
}

function applySearch() {
  appliedSearch.value = search.value.trim();
  page.value = 1;
  fetchData();
}

function clearSearch() {
  search.value = "";
  appliedSearch.value = "";
  page.value = 1;
  fetchData();
}

function prev() {
  if (page.value > 1) {
    page.value--;
    fetchData();
  }
}

function next() {
  if (page.value < totalPages.value) {
    page.value++;
    fetchData();
  }
}

function changeLimit() {
  page.value = 1;
  fetchData();
}

onMounted(fetchData);
</script>