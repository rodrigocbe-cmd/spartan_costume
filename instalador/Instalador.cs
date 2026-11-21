// GoW III Costumes - instalador (Windows Forms, .NET Framework 4, C# 5).
// Compilado pelo ferramentas/build.py com o csc.exe do Windows; os dados do pacote
// (dados/manifest.json, deltas .gw3d e previews) vão embutidos como recursos "dados/<arquivo>".
//
// Cada visual entra num SLOT NOVO do menu de trajes (R_HERO09, 10, ... em sequência). Os arquivos são
// montados a partir dos arquivos ORIGINAIS do jogo do usuário + deltas (o pacote não tem arquivos do jogo).
// SpartanPort: um único mod "GoW3 Costumes" na pasta de mods. PS4: pasta EXEC para copiar ao console.
//
// Linha de comando (testes): --acao instalar|remover|ps4 --ids a,b|todos [--spartan X] [--jogo X]
//                            [--mods X] [--saida X] [--sim]
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;

[assembly: AssemblyTitle("GoW III Costumes")]
[assembly: AssemblyProduct("GoW III Costumes")]

namespace GoW3Costumes
{
    // ------------------------------------------------------------------ textos (tabela por idioma)
    static class Txt
    {
        public static string Lang = (CultureInfo.CurrentUICulture.Name.StartsWith("pt", StringComparison.OrdinalIgnoreCase)
            || CultureInfo.CurrentCulture.Name.StartsWith("pt", StringComparison.OrdinalIgnoreCase)) ? "pt" : "en";

        static readonly Dictionary<string, Dictionary<string, string>> T = new Dictionary<string, Dictionary<string, string>>
        {
            { "pt", new Dictionary<string, string> {
                { "titulo", "GoW III Costumes {0}" },
                { "subtitulo", "Visuais novos para o Kratos em God of War III Remastered. Cada visual entra como um traje novo no menu de trajes; o jogo original nunca é alterado." },
                { "pasta", "Pasta do jogo (SpartanPort)" },
                { "procurar", "Procurar..." },
                { "visuais", "Visuais (marque os que quer instalar)" },
                { "aplicar", "Instalar / atualizar" },
                { "remover_tudo", "Remover tudo" },
                { "ps4", "Gerar arquivos para PS4..." },
                { "sair", "Fechar" },
                { "sel_spartan", "Selecione a pasta do jogo (a pasta do SpartanPort, onde está o SpartanPort.exe)." },
                { "sel_jogo", "Selecione a pasta com os arquivos do jogo (a que tem eboot.bin e a pasta EXEC)." },
                { "sel_saida", "Escolha onde salvar os arquivos para PS4." },
                { "pasta_ok", "SpartanPort encontrado. Arquivos do jogo: {0}" },
                { "pasta_sem_jogo", "SpartanPort encontrado, mas a pasta dos arquivos do jogo não foi encontrada (será perguntada)." },
                { "pasta_invalida", "Esta pasta não tem o SpartanPort.exe. Use \"Procurar...\" para escolher a pasta do jogo." },
                { "instalado_em", "Instalado: {0}" },
                { "nada_instalado", "Nenhum visual instalado." },
                { "slot", "{0} (traje {1})" },
                { "sem_slot", "{0} (vale para todos os trajes)" },
                { "montando", "Montando {0}..." },
                { "pulando", "Pulando {0} (não existe no seu jogo; DLC não instalada?)" },
                { "hash_dif", "O arquivo {0} do seu jogo é diferente do esperado (versão ou região diferente?).\n\nContinuar mesmo assim?" },
                { "verif_dif", "AVISO: {0} gerado difere do esperado." },
                { "sem_wad", "Arquivo original não encontrado: {0}" },
                { "cancelado", "Cancelado." },
                { "antigo", "Removendo instalação antiga: {0}" },
                { "conflito", "AVISO: o mod \"{0}\" também altera {1}. No SpartanPort, o mod mais abaixo na lista vence." },
                { "pronto", "Pronto! Visuais instalados no mod \"{0}\":" },
                { "pronto2", "Abra o SpartanPort, aba Mods, e confira se o mod \"{0}\" está ativado. No jogo: menu Extras > Seleção de traje." },
                { "removido_tudo", "Todos os visuais foram removidos (mod \"{0}\" apagado)." },
                { "ps4_ok", "Arquivos para PS4 gerados em:\n{0}\n\nCopie a pasta EXEC para o PS4 com um redirecionador de arquivos (ex.: plugin AFR do GoldHEN: /data/GoldHEN/AFR/<ID do jogo>/EXEC/)." },
                { "erro", "ERRO: {0}" },
                { "erro_titulo", "Erro" },
                { "permissao", "Sem permissão para gravar em {0}. Tente executar o instalador como administrador." },
                { "concluido", "Concluído" },
                { "nenhum_marcado", "Nenhum visual marcado. Remover todos os visuais instalados?" },
                { "confirmar_remover", "Remover todos os visuais do GoW III Costumes?" },
                { "trabalhando", "Aguarde..." },
            } },
            { "en", new Dictionary<string, string> {
                { "titulo", "GoW III Costumes {0}" },
                { "subtitulo", "New Kratos costumes for God of War III Remastered. Each costume is added as a new entry in the costume menu; the original game is never modified." },
                { "pasta", "Game folder (SpartanPort)" },
                { "procurar", "Browse..." },
                { "visuais", "Costumes (check the ones you want installed)" },
                { "aplicar", "Install / update" },
                { "remover_tudo", "Remove all" },
                { "ps4", "Build files for PS4..." },
                { "sair", "Close" },
                { "sel_spartan", "Select the game folder (the SpartanPort folder, with SpartanPort.exe)." },
                { "sel_jogo", "Select the folder with the game files (the one with eboot.bin and the EXEC folder)." },
                { "sel_saida", "Choose where to save the PS4 files." },
                { "pasta_ok", "SpartanPort found. Game files: {0}" },
                { "pasta_sem_jogo", "SpartanPort found, but the game files folder was not found (you will be asked)." },
                { "pasta_invalida", "This folder does not contain SpartanPort.exe. Use \"Browse...\" to choose the game folder." },
                { "instalado_em", "Installed: {0}" },
                { "nada_instalado", "No costume installed." },
                { "slot", "{0} (costume {1})" },
                { "sem_slot", "{0} (applies to all costumes)" },
                { "montando", "Building {0}..." },
                { "pulando", "Skipping {0} (not in your game; DLC not installed?)" },
                { "hash_dif", "File {0} in your game differs from the expected one (different version or region?).\n\nContinue anyway?" },
                { "verif_dif", "WARNING: built {0} differs from the expected file." },
                { "sem_wad", "Original file not found: {0}" },
                { "cancelado", "Cancelled." },
                { "antigo", "Removing old installation: {0}" },
                { "conflito", "WARNING: mod \"{0}\" also changes {1}. In SpartanPort, the lower mod in the list wins." },
                { "pronto", "Done! Costumes installed in mod \"{0}\":" },
                { "pronto2", "Open SpartanPort, Mods tab, and make sure mod \"{0}\" is enabled. In game: Extras menu > Costume selection." },
                { "removido_tudo", "All costumes were removed (mod \"{0}\" deleted)." },
                { "ps4_ok", "PS4 files built in:\n{0}\n\nCopy the EXEC folder to the PS4 with a file redirector (e.g. GoldHEN AFR plugin: /data/GoldHEN/AFR/<game ID>/EXEC/)." },
                { "erro", "ERROR: {0}" },
                { "erro_titulo", "Error" },
                { "permissao", "No permission to write to {0}. Try running the installer as administrator." },
                { "concluido", "Done" },
                { "nenhum_marcado", "No costume checked. Remove all installed costumes?" },
                { "confirmar_remover", "Remove all GoW III Costumes costumes?" },
                { "trabalhando", "Please wait..." },
            } },
        };

        public static string S(string k) { return T[Lang][k]; }
        public static string F(string k, params object[] a) { return string.Format(S(k), a); }
    }

    // ------------------------------------------------------------------ pacote embutido
    class Pacote
    {
        public Dictionary<string, object> Man;
        public List<Dictionary<string, object>> Trajes = new List<Dictionary<string, object>>();
        public string Versao;

        public static byte[] Recurso(string nome)
        {
            using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("dados/" + nome))
            {
                if (s == null) throw new Exception("dados/" + nome + "?");
                MemoryStream ms = new MemoryStream();
                s.CopyTo(ms);
                return ms.ToArray();
            }
        }

        public Pacote()
        {
            JavaScriptSerializer js = new JavaScriptSerializer();
            js.MaxJsonLength = int.MaxValue;
            Man = (Dictionary<string, object>)js.DeserializeObject(Encoding.UTF8.GetString(Recurso("manifest.json")).TrimStart('\uFEFF'));
            foreach (object o in (object[])Man["trajes"]) Trajes.Add((Dictionary<string, object>)o);
            Versao = (string)Man["versao"];
        }

        public static string Nome(Dictionary<string, object> t)
        {
            Dictionary<string, object> n = (Dictionary<string, object>)t["nomes"];
            return n.ContainsKey(Txt.Lang) ? (string)n[Txt.Lang] : (string)n["en"];
        }

        public static string Descricao(Dictionary<string, object> t)
        {
            Dictionary<string, object> n = (Dictionary<string, object>)t["descricao"];
            return n.ContainsKey(Txt.Lang) ? (string)n[Txt.Lang] : (string)n["en"];
        }

        public static bool TemSlot(Dictionary<string, object> t)
        {
            return !t.ContainsKey("slot") || !(t["slot"] is bool) || (bool)t["slot"];
        }

        public Dictionary<string, object> Traje(string id)
        {
            foreach (Dictionary<string, object> t in Trajes) if ((string)t["id"] == id) return t;
            throw new Exception("costume '" + id + "'?");
        }

        public List<string> Ordenar(IEnumerable<string> ids)
        {
            HashSet<string> h = new HashSet<string>(ids);
            List<string> r = new List<string>();
            foreach (Dictionary<string, object> t in Trajes) if (h.Contains((string)t["id"])) r.Add((string)t["id"]);
            return r;
        }
    }

    // ------------------------------------------------------------------ montagem dos arquivos
    class Motor
    {
        public const string PastaMod = "GoW3 Costumes";
        public const string Marcador = "gow3costume.json";
        public Action<string> Log = delegate { };
        public Func<string, bool> Perguntar = delegate { return true; };
        public Action<int, int> Progresso = delegate { };
        readonly Pacote P;
        readonly Dictionary<string, byte[]> fontes = new Dictionary<string, byte[]>();
        readonly Dictionary<string, string> shaFontes = new Dictionary<string, string>();
        readonly HashSet<string> avisados = new HashSet<string>();
        int feitos, total;

        public Motor(Pacote p) { P = p; }

        public static string Sha(byte[] b)
        {
            using (SHA256 h = SHA256.Create()) return BitConverter.ToString(h.ComputeHash(b)).Replace("-", "").ToLowerInvariant();
        }

        public static byte[] AplicarDelta(byte[] orig, byte[] d)
        {
            // 'GW3D' u32 versão u64 tamanho u32 n_ops u32 0 | n_ops x (i64 origem [-1 = literal], u32 tam, u32 0) | literais
            if (Encoding.ASCII.GetString(d, 0, 4) != "GW3D") throw new Exception("delta?");
            long n = BitConverter.ToInt64(d, 8);
            int nops = BitConverter.ToInt32(d, 16);
            byte[] o = new byte[n];
            long lit = 24 + 16L * nops, pos = 0;
            for (int i = 0; i < nops; i++)
            {
                long s = BitConverter.ToInt64(d, 24 + 16 * i);
                int t = BitConverter.ToInt32(d, 32 + 16 * i);
                if (s < 0) { Array.Copy(d, lit, o, pos, t); lit += t; }
                else Array.Copy(orig, s, o, pos, t);
                pos += t;
            }
            if (pos != n) throw new Exception("delta: tamanho");
            return o;
        }

        static string Str(Dictionary<string, object> d, string k) { return d.ContainsKey(k) && d[k] != null ? d[k].ToString() : ""; }

        byte[] Fonte(string jogo, string rel)
        {
            if (!fontes.ContainsKey(rel))
            {
                string p = Path.Combine(jogo, "EXEC", rel.Replace('/', '\\'));
                if (!File.Exists(p)) return null;
                byte[] b = File.ReadAllBytes(p);
                fontes[rel] = b;
                shaFontes[rel] = Sha(b);
            }
            return fontes[rel];
        }

        string GravarItem(Dictionary<string, object> it, string destRel, string jogo, string saida)
        {
            string fonte = Str(it, "fonte");
            byte[] f = Fonte(jogo, fonte);
            feitos++; Progresso(feitos, total);
            if (f == null)
            {
                if (it.ContainsKey("opcional") && it["opcional"] is bool && (bool)it["opcional"]) { Log(Txt.F("pulando", fonte)); return null; }
                throw new Exception(Txt.F("sem_wad", fonte));
            }
            if (shaFontes[fonte] != Str(it, "sha256_fonte") && !avisados.Contains(fonte))
            {
                avisados.Add(fonte);
                if (!Perguntar(Txt.F("hash_dif", fonte))) throw new OperationCanceledException(Txt.S("cancelado"));
            }
            Log(Txt.F("montando", destRel));
            byte[] novo = AplicarDelta(f, Pacote.Recurso(Str(it, "delta")));
            if (Sha(novo) != Str(it, "sha256_resultado")) Log(Txt.F("verif_dif", destRel));
            string p = Path.Combine(saida, "EXEC", destRel.Replace('/', '\\'));
            Directory.CreateDirectory(Path.GetDirectoryName(p));
            File.WriteAllBytes(p, novo);
            return destRel;
        }

        // grava em <saida>\EXEC\... os arquivos dos visuais ids; devolve as linhas de resumo e os arquivos
        public List<string> Montar(List<string> idsEnt, string jogo, string saida, List<string> arquivos)
        {
            List<string> ids = P.Ordenar(idsEnt);
            string exec = Path.Combine(saida, "EXEC");
            if (Directory.Exists(exec)) Directory.Delete(exec, true);
            List<string> resumo = new List<string>();
            List<string> comSlot = new List<string>();
            int idx = Convert.ToInt32(P.Man["primeiro_indice"]);
            total = 0; feitos = 0;
            foreach (string id in ids) total += ((object[])P.Traje(id)["arquivos"]).Length;
            Dictionary<string, object> comp = (Dictionary<string, object>)P.Man["compartilhados"];
            string chave0 = string.Join("+", ids.Where(i => Pacote.TemSlot(P.Traje(i))).ToArray());
            if (chave0.Length > 0) total += ((object[])comp[chave0]).Length;
            foreach (string id in ids)
            {
                Dictionary<string, object> c = P.Traje(id);
                bool temSlot = Pacote.TemSlot(c);
                foreach (object o in (object[])c["arquivos"])
                {
                    Dictionary<string, object> it = (Dictionary<string, object>)o;
                    string dest = Str(it, "destino");
                    if (dest == "slot") dest = string.Format("WAD/PS4_LE/R_HERO{0:D2}.WAD", idx);
                    else if (!dest.Contains("/")) dest = "WAD/PS4_LE/" + dest;
                    string r = GravarItem(it, dest, jogo, saida);
                    if (r != null) arquivos.Add(r);
                }
                if (temSlot)
                {
                    resumo.Add(Txt.F("slot", Pacote.Nome(c), string.Format("R_HERO{0:D2}", idx)));
                    comSlot.Add(id);
                    idx++;
                }
                else resumo.Add(Txt.F("sem_slot", Pacote.Nome(c)));
            }
            string chave = string.Join("+", comSlot.ToArray());
            if (chave.Length > 0)
            {
                foreach (object o in (object[])comp[chave])
                {
                    Dictionary<string, object> it = (Dictionary<string, object>)o;
                    string r = GravarItem(it, Str(it, "destino"), jogo, saida);
                    if (r != null) arquivos.Add(r);
                }
            }
            fontes.Clear(); shaFontes.Clear();
            return resumo;
        }

        // ---------------------------------------------- SpartanPort
        public static Dictionary<string, object> LerJson(string arq)
        {
            try
            {
                if (!File.Exists(arq)) return null;
                return (Dictionary<string, object>)new JavaScriptSerializer().DeserializeObject(File.ReadAllText(arq, Encoding.UTF8));
            }
            catch { return null; }
        }

        public static string JogoDasConfiguracoes(string sp)
        {
            Dictionary<string, object> cfg = LerJson(Path.Combine(sp, "settings.json"));
            if (cfg != null && cfg.ContainsKey("game_dir") && cfg["game_dir"] != null)
            {
                string g = cfg["game_dir"].ToString();
                if (g.Length > 0 && Directory.Exists(Path.Combine(g, "EXEC", "WAD", "PS4_LE"))) return g;
            }
            return null;
        }

        public static string PastaMods(string sp)
        {
            Dictionary<string, object> cfg = LerJson(Path.Combine(sp, "settings.json"));
            if (cfg != null && cfg.ContainsKey("mods_dir") && cfg["mods_dir"] != null && cfg["mods_dir"].ToString().Length > 0)
                return cfg["mods_dir"].ToString();
            return Path.Combine(sp, "mods");
        }

        public static bool EhSpartan(string p) { return !string.IsNullOrEmpty(p) && File.Exists(Path.Combine(p, "SpartanPort.exe")); }
        public static bool EhJogo(string p) { return !string.IsNullOrEmpty(p) && Directory.Exists(Path.Combine(p, "EXEC", "WAD", "PS4_LE")); }

        public static string DetectarSpartan()
        {
            List<string> cand = new List<string>();
            string p = AppDomain.CurrentDomain.BaseDirectory;
            for (int i = 0; i < 4 && !string.IsNullOrEmpty(p); i++) { cand.Add(p); p = Path.GetDirectoryName(p.TrimEnd('\\')); }
            string perfil = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            foreach (string b in new[] { @"C:\Games", @"D:\Games", @"E:\Games", Path.Combine(perfil, "Games"), Path.Combine(perfil, "Downloads"),
                                         Path.Combine(perfil, "Desktop"), @"C:\Program Files", @"C:\Program Files (x86)" })
            {
                try { if (Directory.Exists(b)) cand.AddRange(Directory.GetDirectories(b)); } catch { }
            }
            foreach (string c in cand) if (EhSpartan(c)) return c;
            return null;
        }

        public static List<string> Instalados(string mods)
        {
            Dictionary<string, object> m = LerJson(Path.Combine(mods, PastaMod, Marcador));
            List<string> r = new List<string>();
            if (m != null && m.ContainsKey("ids") && m["ids"] is object[]) foreach (object o in (object[])m["ids"]) r.Add(o.ToString());
            return r;
        }

        public static void LimparModsJson(string sp, string nomePasta)
        {
            string f = Path.Combine(sp, "mods.json");
            Dictionary<string, object> j = LerJson(f);
            if (j == null) return;
            foreach (string k in new[] { "order", "disabled" })
                if (j.ContainsKey(k) && j[k] is object[]) j[k] = ((object[])j[k]).Where(x => x == null || x.ToString() != nomePasta).ToArray();
            File.WriteAllText(f, new JavaScriptSerializer().Serialize(j), new UTF8Encoding(false));
        }

        void RemoverAntigos(string mods, string sp)
        {
            // instalações do instalador antigo (uma pasta por visual, substituindo um slot do jogo)
            if (!Directory.Exists(mods)) return;
            foreach (string d in Directory.GetDirectories(mods))
            {
                string nome = Path.GetFileName(d);
                if (nome != PastaMod && File.Exists(Path.Combine(d, Marcador)))
                {
                    Log(Txt.F("antigo", nome));
                    Directory.Delete(d, true);
                    if (sp != null) LimparModsJson(sp, nome);
                }
            }
        }

        public List<string> AplicarSpartan(List<string> idsEnt, string jogo, string mods, string sp)
        {
            List<string> ids = P.Ordenar(idsEnt);
            string pasta = Path.Combine(mods, PastaMod);
            RemoverAntigos(mods, sp);
            if (ids.Count == 0)
            {
                if (Directory.Exists(pasta)) Directory.Delete(pasta, true);
                if (sp != null) LimparModsJson(sp, PastaMod);
                Log(Txt.F("removido_tudo", PastaMod));
                return new List<string>();
            }
            Directory.CreateDirectory(pasta);
            List<string> arquivos = new List<string>();
            List<string> resumo = Montar(ids, jogo, pasta, arquivos);
            JavaScriptSerializer js = new JavaScriptSerializer();
            Dictionary<string, object> mj = new Dictionary<string, object>();
            mj["name"] = "GoW III Costumes";
            mj["author"] = Str(P.Traje(ids[0]), "autor");
            mj["version"] = P.Versao;
            mj["description"] = string.Join(", ", ids.Select(i => Pacote.Nome(P.Traje(i))).ToArray());
            File.WriteAllText(Path.Combine(pasta, "mod.json"), js.Serialize(mj), new UTF8Encoding(false));
            string pv = Path.Combine(pasta, "preview.png");
            if (File.Exists(pv)) File.Delete(pv);
            foreach (string id in ids)
            {
                string prev = Str(P.Traje(id), "preview");
                if (prev.Length > 0) { File.WriteAllBytes(pv, Pacote.Recurso(prev)); break; }
            }
            Dictionary<string, object> mk = new Dictionary<string, object>();
            mk["ids"] = ids.ToArray();
            mk["versao"] = P.Versao;
            File.WriteAllText(Path.Combine(pasta, Marcador), js.Serialize(mk), new UTF8Encoding(false));
            foreach (string outro in Directory.GetDirectories(mods))
            {
                if (Path.GetFileName(outro) == PastaMod) continue;
                foreach (string a in arquivos)
                    if (File.Exists(Path.Combine(outro, "EXEC", a.Replace('/', '\\')))) Log(Txt.F("conflito", Path.GetFileName(outro), a));
            }
            return resumo;
        }
    }

    // ------------------------------------------------------------------ janela
    class Janela : Form
    {
        readonly Pacote P;
        TextBox txtPasta, txtLog;
        Label lblStatus, lblDesc;
        CheckedListBox lista;
        Button btnAplicar, btnRemover, btnPS4, btnProcurar;
        ProgressBar barra;
        string sp, jogo, mods;

        public Janela(Pacote p)
        {
            P = p;
            Text = Txt.F("titulo", P.Versao);
            Font = new Font("Segoe UI", 9f);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(680, 600);
            MinimumSize = new Size(560, 480);
            StartPosition = FormStartPosition.CenterScreen;
            try { Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }
            Padding = new Padding(10);

            Label titulo = new Label { Text = Txt.F("titulo", P.Versao), Dock = DockStyle.Top, Height = 34, Font = new Font("Segoe UI", 15f, FontStyle.Bold) };
            Label sub = new Label { Text = Txt.S("subtitulo"), Dock = DockStyle.Top, Height = 40 };

            GroupBox grpPasta = new GroupBox { Text = Txt.S("pasta"), Dock = DockStyle.Top, Height = 104, Padding = new Padding(8) };
            TableLayoutPanel tp = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, RowCount = 2 };
            tp.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
            tp.ColumnStyles.Add(new ColumnStyle(SizeType.AutoSize));
            tp.RowStyles.Add(new RowStyle(SizeType.AutoSize));
            tp.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            txtPasta = new TextBox { Dock = DockStyle.Fill };
            txtPasta.Leave += delegate { AtualizarPasta(); };
            txtPasta.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) AtualizarPasta(); };
            btnProcurar = new Button { Text = Txt.S("procurar"), AutoSize = true };
            btnProcurar.Click += delegate { Procurar(); };
            lblStatus = new Label { Dock = DockStyle.Fill, AutoEllipsis = true };
            tp.Controls.Add(txtPasta, 0, 0); tp.Controls.Add(btnProcurar, 1, 0);
            tp.Controls.Add(lblStatus, 0, 1); tp.SetColumnSpan(lblStatus, 2);
            grpPasta.Controls.Add(tp);

            GroupBox grpVis = new GroupBox { Text = Txt.S("visuais"), Dock = DockStyle.Top, Height = 170, Padding = new Padding(8) };
            lista = new CheckedListBox { Dock = DockStyle.Top, Height = 64, CheckOnClick = true, IntegralHeight = false };
            foreach (Dictionary<string, object> t in P.Trajes) lista.Items.Add(Pacote.Nome(t), true);
            lista.SelectedIndexChanged += delegate { MostrarDescricao(); };
            lblDesc = new Label { Dock = DockStyle.Fill, Padding = new Padding(0, 6, 0, 0) };
            grpVis.Controls.Add(lblDesc); grpVis.Controls.Add(lista);

            FlowLayoutPanel botoes = new FlowLayoutPanel { Dock = DockStyle.Top, Height = 42, Padding = new Padding(0, 6, 0, 0) };
            btnAplicar = new Button { Text = Txt.S("aplicar"), AutoSize = true, Font = new Font("Segoe UI", 9f, FontStyle.Bold) };
            btnRemover = new Button { Text = Txt.S("remover_tudo"), AutoSize = true };
            btnPS4 = new Button { Text = Txt.S("ps4"), AutoSize = true };
            btnAplicar.Click += delegate { Aplicar(); };
            btnRemover.Click += delegate { RemoverTudo(); };
            btnPS4.Click += delegate { GerarPS4(); };
            botoes.Controls.AddRange(new Control[] { btnAplicar, btnRemover, btnPS4 });

            barra = new ProgressBar { Dock = DockStyle.Top, Height = 16 };
            txtLog = new TextBox { Dock = DockStyle.Fill, Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, BackColor = SystemColors.Window };

            // ordem de Dock: o último adicionado fica no topo
            Controls.Add(txtLog); Controls.Add(barra); Controls.Add(botoes); Controls.Add(grpVis);
            Controls.Add(grpPasta); Controls.Add(sub); Controls.Add(titulo);

            AcceptButton = btnAplicar;
            Shown += delegate
            {
                txtPasta.Text = Motor.DetectarSpartan() ?? "";
                AtualizarPasta();
                if (lista.Items.Count > 0) lista.SelectedIndex = 0;
            };
        }

        void Log(string s)
        {
            if (InvokeRequired) { BeginInvoke(new Action<string>(Log), s); return; }
            txtLog.AppendText(s.Replace("\n", "\r\n") + "\r\n");
        }

        void MostrarDescricao()
        {
            int i = lista.SelectedIndex;
            lblDesc.Text = i >= 0 ? Pacote.Descricao(P.Trajes[i]) : "";
        }

        void AtualizarPasta()
        {
            string p = txtPasta.Text.Trim().Trim('"');
            sp = null; jogo = null; mods = null;
            if (!Motor.EhSpartan(p)) { lblStatus.Text = p.Length > 0 ? Txt.S("pasta_invalida") : Txt.S("sel_spartan"); return; }
            sp = p;
            jogo = Motor.JogoDasConfiguracoes(sp);
            mods = Motor.PastaMods(sp);
            List<string> inst = Motor.Instalados(mods);
            string st = jogo != null ? Txt.F("pasta_ok", jogo) : Txt.S("pasta_sem_jogo");
            st += "\n" + (inst.Count > 0 ? Txt.F("instalado_em", string.Join(", ", inst.Select(i => Pacote.Nome(P.Traje(i))).ToArray()))
                                         : Txt.S("nada_instalado"));
            lblStatus.Text = st;
            if (inst.Count > 0)
                for (int i = 0; i < P.Trajes.Count; i++) lista.SetItemChecked(i, inst.Contains((string)P.Trajes[i]["id"]));
        }

        string EscolherPasta(string msg, string inicial)
        {
            using (FolderBrowserDialog d = new FolderBrowserDialog())
            {
                d.Description = msg;
                d.ShowNewFolderButton = false;
                if (!string.IsNullOrEmpty(inicial) && Directory.Exists(inicial)) d.SelectedPath = inicial;
                return d.ShowDialog(this) == DialogResult.OK ? d.SelectedPath : null;
            }
        }

        void Procurar()
        {
            while (true)
            {
                string p = EscolherPasta(Txt.S("sel_spartan"), txtPasta.Text);
                if (p == null) return;
                txtPasta.Text = p;
                AtualizarPasta();
                if (sp != null) return;
                MessageBox.Show(this, Txt.S("pasta_invalida"), Text, MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        bool GarantirPastas()
        {
            AtualizarPasta();
            if (sp == null) { Procurar(); if (sp == null) return false; }
            while (jogo == null)
            {
                string g = EscolherPasta(Txt.S("sel_jogo"), null);
                if (g == null) return false;
                if (Motor.EhJogo(g)) jogo = g;
            }
            return true;
        }

        List<string> Marcados()
        {
            List<string> r = new List<string>();
            for (int i = 0; i < P.Trajes.Count; i++) if (lista.GetItemChecked(i)) r.Add((string)P.Trajes[i]["id"]);
            return r;
        }

        void Ocupado(bool sim)
        {
            foreach (Control c in new Control[] { btnAplicar, btnRemover, btnPS4, btnProcurar, txtPasta, lista }) c.Enabled = !sim;
            UseWaitCursor = sim;
            if (!sim) barra.Value = 0;
        }

        Motor NovoMotor()
        {
            Motor m = new Motor(P);
            m.Log = Log;
            m.Progresso = (a, b) => BeginInvoke(new Action(() => { barra.Maximum = Math.Max(1, b); barra.Value = Math.Min(a, barra.Maximum); }));
            m.Perguntar = s => (bool)Invoke(new Func<bool>(() =>
                MessageBox.Show(this, s, Text, MessageBoxButtons.YesNo, MessageBoxIcon.Warning) == DialogResult.Yes));
            return m;
        }

        void Executar(Func<string> trabalho)
        {
            Ocupado(true);
            Log(Txt.S("trabalhando"));
            Thread t = new Thread(() =>
            {
                string fim = null, erro = null;
                try { fim = trabalho(); }
                catch (OperationCanceledException ex) { erro = ex.Message; }
                catch (UnauthorizedAccessException ex) { erro = Txt.F("permissao", mods ?? "") + "\n" + ex.Message; }
                catch (Exception ex) { erro = ex.Message; }
                BeginInvoke(new Action(() =>
                {
                    Ocupado(false);
                    if (erro != null)
                    {
                        Log(Txt.F("erro", erro));
                        MessageBox.Show(this, erro, Txt.S("erro_titulo"), MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                    else
                    {
                        Log(fim);
                        AtualizarPasta();
                        MessageBox.Show(this, fim, Txt.S("concluido"), MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                }));
            });
            t.IsBackground = true;
            t.Start();
        }

        void Aplicar()
        {
            if (!GarantirPastas()) return;
            List<string> ids = Marcados();
            if (ids.Count == 0 && MessageBox.Show(this, Txt.S("nenhum_marcado"), Text, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
            string j = jogo, m = mods, s = sp;
            Executar(() =>
            {
                List<string> resumo = NovoMotor().AplicarSpartan(ids, j, m, s);
                if (ids.Count == 0) return Txt.F("removido_tudo", Motor.PastaMod);
                return Txt.F("pronto", Motor.PastaMod) + "\n  " + string.Join("\n  ", resumo.ToArray()) + "\n\n" + Txt.F("pronto2", Motor.PastaMod);
            });
        }

        void RemoverTudo()
        {
            AtualizarPasta();
            if (sp == null) { Procurar(); if (sp == null) return; }
            if (MessageBox.Show(this, Txt.S("confirmar_remover"), Text, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
            string m = mods, s = sp;
            Executar(() => { NovoMotor().AplicarSpartan(new List<string>(), null, m, s); return Txt.F("removido_tudo", Motor.PastaMod); });
        }

        void GerarPS4()
        {
            string g = jogo;
            while (true)
            {
                g = EscolherPasta(Txt.S("sel_jogo"), g);
                if (g == null) return;
                if (Motor.EhJogo(g)) break;
            }
            string saida = EscolherPasta(Txt.S("sel_saida"), Environment.GetFolderPath(Environment.SpecialFolder.Desktop));
            if (saida == null) return;
            saida = Path.Combine(saida, "GoW3 Costumes PS4");
            List<string> ids = Marcados();
            if (ids.Count == 0) ids = P.Trajes.Select(t => (string)t["id"]).ToList();
            Executar(() =>
            {
                Directory.CreateDirectory(saida);
                List<string> resumo = NovoMotor().Montar(ids, g, saida, new List<string>());
                return Txt.F("ps4_ok", Path.Combine(saida, "EXEC")) + "\n\n  " + string.Join("\n  ", resumo.ToArray());
            });
        }
    }

    // ------------------------------------------------------------------ entrada
    static class Programa
    {
        [STAThread]
        static int Main(string[] args)
        {
            Pacote p;
            try { p = new Pacote(); }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "GoW III Costumes", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return 1;
            }
            if (args.Length > 0) return LinhaDeComando(p, args);
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Janela(p));
            return 0;
        }

        static int LinhaDeComando(Pacote p, string[] args)
        {
            Dictionary<string, string> a = new Dictionary<string, string>();
            for (int i = 0; i < args.Length; i++)
            {
                if (!args[i].StartsWith("--")) continue;
                string k = args[i].Substring(2);
                a[k] = (i + 1 < args.Length && !args[i + 1].StartsWith("--")) ? args[++i] : "1";
            }
            Func<string, string> A = k => a.ContainsKey(k) ? a[k] : null;
            try
            {
                Motor m = new Motor(p);
                m.Log = Console.WriteLine;
                m.Perguntar = s => { Console.WriteLine(s); return A("sim") != null; };
                List<string> ids = (A("ids") ?? "todos") == "todos" ? p.Trajes.Select(t => (string)t["id"]).ToList()
                                                                      : A("ids").Split(',').Select(x => x.Trim()).Where(x => x.Length > 0).ToList();
                foreach (string id in ids) p.Traje(id);
                string acao = A("acao") ?? "";
                if (acao == "ps4")
                {
                    List<string> r = m.Montar(ids, A("jogo"), A("saida"), new List<string>());
                    foreach (string l in r) Console.WriteLine(l);
                    return 0;
                }
                string sp = A("spartan");
                string jogo = A("jogo") ?? (sp != null ? Motor.JogoDasConfiguracoes(sp) : null);
                string mods = A("mods") ?? (sp != null ? Motor.PastaMods(sp) : null);
                if (mods == null) throw new Exception("--mods?");
                List<string> atuais = Motor.Instalados(mods);
                List<string> alvo = acao == "remover" ? atuais.Where(x => !ids.Contains(x)).ToList() : atuais.Union(ids).ToList();
                if (acao != "remover" && acao != "instalar") throw new Exception("--acao?");
                if (alvo.Count > 0 && !Motor.EhJogo(jogo)) throw new Exception("--jogo?");
                foreach (string l in m.AplicarSpartan(alvo, jogo, mods, sp)) Console.WriteLine(l);
                return 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERRO: " + ex);
                return 1;
            }
        }
    }
}
