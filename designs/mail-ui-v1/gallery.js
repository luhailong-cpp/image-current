"use strict";

const grid = document.getElementById("festival-grid");
const count = document.getElementById("gallery-count");
const dialog = document.getElementById("art-dialog");
const search = document.getElementById("festival-search");
const selection = { group: "all", season: "all", query: "" };
let catalog;
let returnFocus;

function openArt(event, trigger) {
  document.getElementById("art-title").textContent = event.name + " · " + event.title;
  const image = document.getElementById("art-image");
  image.src = "assets/" + event.image;
  image.alt = event.alt;
  document.getElementById("original-link").href = image.src;
  document.getElementById("mail-preview-link").href = "index.html?festival=" + encodeURIComponent(event.id);
  returnFocus = trigger;
  dialog.showModal();
}

function makeCard(event) {
  const article = document.createElement("article");
  article.className = "festival-card";
  article.dataset.festival = event.id;
  const view = document.createElement("button");
  view.type = "button";
  view.className = "view-art";
  view.setAttribute("aria-label", "查看" + event.name + "插画");
  const image = document.createElement("img");
  image.src = "assets/" + event.image;
  image.alt = event.alt;
  image.width = 2098;
  image.height = 749;
  image.loading = "lazy";
  image.decoding = "async";
  view.append(image);
  view.addEventListener("click", () => openArt(event, view));
  const copy = document.createElement("div");
  copy.className = "card-copy";
  const heading = document.createElement("div");
  heading.className = "card-heading";
  const title = document.createElement("h2");
  title.textContent = event.name;
  const kind = document.createElement("span");
  kind.className = "card-kind";
  kind.textContent = event.groups.map(group => group === "traditional" ? "传统节日" : "节气").join(" · ");
  heading.append(title, kind);
  const tagline = document.createElement("p");
  tagline.className = "card-tagline";
  tagline.textContent = event.tagline;
  const actions = document.createElement("div");
  actions.className = "card-actions";
  const inspect = document.createElement("button");
  inspect.type = "button";
  inspect.textContent = "展开插画";
  inspect.addEventListener("click", () => openArt(event, inspect));
  const link = document.createElement("a");
  link.href = "index.html?festival=" + encodeURIComponent(event.id);
  link.textContent = "放入仙笺";
  link.setAttribute("aria-label", "查看" + event.name + "邮件效果");
  actions.append(inspect, link);
  copy.append(heading, tagline, actions);
  article.append(view, copy);
  return article;
}

function renderGallery() {
  const order = selection.group === "solar" ? catalog.solarOrder :
    selection.group === "traditional" ? catalog.traditionalOrder :
    [...catalog.traditionalOrder, ...catalog.solarOrder.filter(id => !catalog.traditionalOrder.includes(id))];
  const events = order.map(id => catalog.festivals.find(event => event.id === id)).filter(event =>
    (selection.season === "all" || event.season === selection.season) &&
    (!selection.query || (event.name + event.title + event.tagline).includes(selection.query)));
  grid.replaceChildren(...events.map(makeCard));
  count.textContent = "共 " + events.length + " 幅";
  document.getElementById("gallery-empty").hidden = events.length > 0;
  document.querySelectorAll("[data-group]").forEach(button => button.setAttribute("aria-pressed", button.dataset.group === selection.group));
  document.querySelectorAll("[data-season]").forEach(button => button.setAttribute("aria-pressed", button.dataset.season === selection.season));
}

document.querySelectorAll("[data-group]").forEach(button => button.addEventListener("click", () => {
  selection.group = button.dataset.group;
  renderGallery();
}));
document.querySelectorAll("[data-season]").forEach(button => button.addEventListener("click", () => {
  selection.season = button.dataset.season;
  renderGallery();
}));
search.addEventListener("input", () => {
  selection.query = search.value.trim();
  renderGallery();
});
document.getElementById("close-art").addEventListener("click", () => dialog.close());
dialog.addEventListener("close", () => returnFocus?.isConnected && returnFocus.focus());
dialog.addEventListener("click", event => {
  if (event.target !== dialog) return;
  const box = dialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
});
fetch("festivals.json").then(response => {
  if (!response.ok) throw new Error("节日目录加载失败");
  return response.json();
}).then(data => {
  catalog = data;
  renderGallery();
}).catch(error => {
  count.textContent = "画卷暂未展开，请通过本地预览服务器打开页面后重试。";
  console.error(error);
});
