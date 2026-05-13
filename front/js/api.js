// ────────────────────────────────────────────────────────────────
// CONFIG API
// ────────────────────────────────────────────────────────────────

const API_URL = "http://localhost:8000/api";

// ────────────────────────────────────────────────────────────────
// TOKEN
// ────────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function removeToken() {
  localStorage.removeItem("access_token");
}

function getUserRole() {
  return localStorage.getItem("userRole");
}

function setUserRole(role) {
  localStorage.setItem("userRole", role);
}

function getUserId() {
  return localStorage.getItem("userId");
}

function setUserId(id) {
  localStorage.setItem("userId", id);
}

// ────────────────────────────────────────────────────────────────
// FETCH BASE
// ────────────────────────────────────────────────────────────────

async function apiFetch(endpoint, options = {}) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    fazerLogout();
    throw new Error("Sessão expirada");
  }

  let data = null;

  try {
    data = await response.json();
  } catch (_) {}

  if (!response.ok) {
    showToastErro(data?.detail);
    throw new Error(data?.detail || "Erro na API");
  }

  return data;
}

// ────────────────────────────────────────────────────────────────
// LOGIN REAL API
// ────────────────────────────────────────────────────────────────

async function realizarLoginAPI(user, pass) {
  try {
    const response = await apiFetch("/usuarios/login", {
      method: "POST",
      body: JSON.stringify({
        email: user,
        senha: pass,
      }),
    });

    setToken(response.access_token);

    setUserId(response.usuario.id_usuario);
    setUserRole(response.usuario.adm ? "admin" : "user");

    return true;
  } catch (err) {
    console.error(err);

    showToast(err);

    return false;
  }
}

// ────────────────────────────────────────────────────────────────
// LOGOUT
// ────────────────────────────────────────────────────────────────

function fazerLogout() {
  localStorage.removeItem("userRole");
  localStorage.removeItem("userId");

  removeToken();

  window.location.href = "../index.html";
}

// ────────────────────────────────────────────────────────────────
// CONTROLE DE ACESSO
// ────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;

  const isPublicPage =
    path.endsWith("index.html") ||
    path.endsWith("/") ||
    path.endsWith("cadastro.html");

  const role = getUserRole();

  if (!role && !isPublicPage) {
    window.location.href = "../index.html";
    return;
  }

  if (role === "user") {
    const telasBloqueadas = [
      "dashboard.html",
      "usuarios.html",
      "produtos.html",
      "categorias.html",
    ];

    const tentouAcessarBloqueada = telasBloqueadas.some((tela) =>
      path.endsWith(tela),
    );

    if (tentouAcessarBloqueada) {
      window.location.href = "loja.html";
    }
  }

  if (role === "admin" && path.endsWith("loja.html")) {
    window.location.href = "dashboard.html";
  }
});

// ────────────────────────────────────────────────────────────────
// TOAST
// ────────────────────────────────────────────────────────────────

function showToast(msg) {
  let container = document.getElementById("toast-container");

  if (!container) {
    container = document.createElement("div");

    container.id = "toast-container";

    container.className = "toast-container";

    document.body.appendChild(container);
  }

  const toast = document.createElement("div");

  toast.className = "toast";

  toast.textContent = msg;

  container.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}

function showToastErro(msg) {
  let container = document.getElementById("toast-container");

  if (!container) {
    container = document.createElement("div");

    container.id = "toast-container";

    container.className = "toast-container";

    document.body.appendChild(container);
  }

  const toast = document.createElement("div");

  toast.className = "toast-erro";

  toast.textContent = msg;

  container.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}

// ────────────────────────────────────────────────────────────────
// USUÁRIOS API
// ────────────────────────────────────────────────────────────────

const Usuarios = {
  listar: async () => {
    return await apiFetch("/usuarios/list");
  },

  criar: async (dados) => {
    return await apiFetch("/usuarios/register", {
      method: "POST",
      body: JSON.stringify(dados),
    });
  },

  editar: async (id, dados) => {
    return await apiFetch(`/usuarios/${id}`, {
      method: "PUT",
      body: JSON.stringify(dados),
    });
  },

  excluir: async (id) => {
    return await apiFetch(`/usuarios/${id}`, {
      method: "DELETE",
    });
  },
};

// ────────────────────────────────────────────────────────────────
// CARRINHO API
// ────────────────────────────────────────────────────────────────

const Carrinho = {
  listar: async (idUsuario) => {
    return await apiFetch(`/carrinho/${idUsuario}`);
  },

  adicionar: async (idUsuario, dados) => {
    return await apiFetch(`/carrinho/${idUsuario}/itens`, {
      method: "POST",
      body: JSON.stringify(dados),
    });
  },

  atualizar: async (idUsuario, idProduto, quantidade) => {
    return await apiFetch(`/carrinho/${idUsuario}/itens/${idProduto}`, {
      method: "PUT",
      body: JSON.stringify({
        quantidade,
      }),
    });
  },

  remover: async (idUsuario, idProduto) => {
    return await apiFetch(`/carrinho/${idUsuario}/itens/${idProduto}`, {
      method: "DELETE",
    });
  },

  finalizar: async (idUsuario) => {
    return await apiFetch(`/checkout`, {
      method: "POST",
      body: JSON.stringify({ id_usuario: idUsuario }),
    });
  },

  limpar: async (idUsuario) => {
    return await apiFetch(`/carrinho/${idUsuario}`, {
      method: "DELETE",
    });
  },
};

// ────────────────────────────────────────────────────────────────
// PRODUTOS API
// ────────────────────────────────────────────────────────────────

const Produtos = {
  listar: async () => {
    return await apiFetch("/produtos");
  },

  criar: async (dados) => {
    return await apiFetch("/produtos", {
      method: "POST",
      body: JSON.stringify(dados),
    });
  },

  editar: async (id, dados) => {
    return await apiFetch(`/produtos/${id}`, {
      method: "PUT",
      body: JSON.stringify(dados),
    });
  },

  excluir: async (id) => {
    return await apiFetch(`/produtos/${id}`, {
      method: "DELETE",
    });
  },
};

// ────────────────────────────────────────────────────────────────
// IMAGENS API
// ────────────────────────────────────────────────────────────────

const Imagem = {
  upload: async (idProduto, file) => {
    const formData = new FormData();
    formData.append("file", file);
    // fetch direto: apiFetch seta Content-Type JSON, incompatível com FormData
    const token = getToken();
    const res = await fetch(`${API_URL}/produtos/${idProduto}/imagem`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erro ${res.status}`);
    }
    return res.json(); // retorna ProdutoOut
  },

  deletar: async (idProduto, imageId) => {
    return await apiFetch(`/produtos/${idProduto}/imagem/${imageId}`, {
      method: "DELETE",
    });
  },

  buscar: (idProduto, imageId) =>
    `${API_URL}/produtos/${idProduto}/imagem/${imageId}`, // URL direta para <img src>
};

// ────────────────────────────────────────────────────────────────
// CATEGORIAS API
// ────────────────────────────────────────────────────────────────

const Categorias = {
  listar: async () => {
    return await apiFetch("/categorias");
  },

  criar: async (dados) => {
    return await apiFetch("/categorias", {
      method: "POST",
      body: JSON.stringify(dados),
    });
  },

  editar: async (id, dados) => {
    return await apiFetch(`/categorias/${id}`, {
      method: "PUT",
      body: JSON.stringify(dados),
    });
  },

  excluir: async (id) => {
    return await apiFetch(`/categorias/${id}`, {
      method: "DELETE",
    });
  },
};

// ────────────────────────────────────────────────────────────────
// REDIS API
// ────────────────────────────────────────────────────────────────

const RedisAPI = {
  listar: async () => {
    return await apiFetch("/redis/cache");
  },

  limparCache: async () => {
    await apiFetch("/redis/cache", {
      method: "DELETE",
    });

    showToast("Cache limpo com sucesso");
  },
};

// ────────────────────────────────────────────────────────────────
// MONGODB API
// ────────────────────────────────────────────────────────────────

const MongoAPI = {
  listar: async () => {
    return await apiFetch("/arquivos");
  },

  upload: async (file) => {
    const formData = new FormData();

    formData.append("file", file);

    const token = getToken();

    const response = await fetch(`${API_URL}/arquivos/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Erro ao enviar arquivo");
    }

    return await response.json();
  },

  excluir: async (id) => {
    return await apiFetch(`/arquivos/${id}`, {
      method: "DELETE",
    });
  },
};

// ────────────────────────────────────────────────────────────────
// MODAIS
// ────────────────────────────────────────────────────────────────

function openModal(id) {
  document.getElementById(id).classList.add("open");
}

function closeModal(id) {
  document.getElementById(id).classList.remove("open");
}
