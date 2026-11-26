import fs from "fs";
import { geoMercator, geoPath, geoCentroid } from "d3-geo";
const UF = {11:["RO","Rondônia"],12:["AC","Acre"],13:["AM","Amazonas"],14:["RR","Roraima"],15:["PA","Pará"],16:["AP","Amapá"],17:["TO","Tocantins"],21:["MA","Maranhão"],22:["PI","Piauí"],23:["CE","Ceará"],24:["RN","Rio Grande do Norte"],25:["PB","Paraíba"],26:["PE","Pernambuco"],27:["AL","Alagoas"],28:["SE","Sergipe"],29:["BA","Bahia"],31:["MG","Minas Gerais"],32:["ES","Espírito Santo"],33:["RJ","Rio de Janeiro"],35:["SP","São Paulo"],41:["PR","Paraná"],42:["SC","Santa Catarina"],43:["RS","Rio Grande do Sul"],50:["MS","Mato Grosso do Sul"],51:["MT","Mato Grosso"],52:["GO","Goiás"],53:["DF","Distrito Federal"]};
const REG = {N:[11,12,13,14,15,16,17],NE:[21,22,23,24,25,26,27,28,29],SE:[31,32,33,35],S:[41,42,43],CO:[50,51,52,53]};
const geo = JSON.parse(fs.readFileSync("br.json"));
// geoJSON do IBGE vem no sentido anti-horário; d3 quer horário — rewind
import { geoArea } from "d3-geo";
for (const f of geo.features) { if (geoArea(f) > 2*Math.PI) { const g=f.geometry; const rev=r=>r.slice().reverse(); if(g.type==="Polygon") g.coordinates=g.coordinates.map(rev); else g.coordinates=g.coordinates.map(p=>p.map(rev)); } }
const W=1000,H=1000;
const proj = geoMercator().fitExtent([[20,20],[W-20,H-20]], geo);
const path = geoPath(proj).digits(1);
const estados = geo.features.map(f => { const c=+f.properties.codarea; const [uf,nome]=UF[c]; const reg=Object.keys(REG).find(k=>REG[k].includes(c)); const [x,y]=proj(geoCentroid(f)); return {uf,nome,reg,d:path(f),cx:+x.toFixed(1),cy:+y.toFixed(1)}; });
const s = proj.scale(), [tx,ty] = proj.translate();
fs.writeFileSync("estados.json", JSON.stringify({W,H,mercator:{scale:+s.toFixed(4),tx:+tx.toFixed(4),ty:+ty.toFixed(4)},estados}));
console.log(estados.length, "estados", (fs.statSync("estados.json").size/1024).toFixed(0)+" KB", "scale", s, tx, ty);
// confere: Fortaleza
console.log("Fortaleza", proj([-38.5267,-3.7319]));
