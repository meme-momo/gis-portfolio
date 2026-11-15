namespace AsiaGIS
{
    partial class GISForm
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(GISForm));
            this.mainmenustrip = new System.Windows.Forms.MenuStrip();
            this.文件ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.打开ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.操作ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.放大ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.缩小ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.漫游ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.全图ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.查询ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.线查询ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.面查询ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.编辑ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.添加线ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.添加面ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.删除线ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.删除面ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.panelbackground = new System.Windows.Forms.Panel();
            this.mainpanel = new System.Windows.Forms.Panel();
            this.maintoolstrip = new System.Windows.Forms.ToolStrip();
            this.toolStripButton打开 = new System.Windows.Forms.ToolStripButton();
            this.toolStripSeparator1 = new System.Windows.Forms.ToolStripSeparator();
            this.toolStripButton箭头 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton放大 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton缩小 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton漫游 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton全图 = new System.Windows.Forms.ToolStripButton();
            this.toolStripSeparator2 = new System.Windows.Forms.ToolStripSeparator();
            this.toolStripButton线查询 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton面查询 = new System.Windows.Forms.ToolStripButton();
            this.toolStripSeparator3 = new System.Windows.Forms.ToolStripSeparator();
            this.toolStripButton添加线 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton添加面 = new System.Windows.Forms.ToolStripButton();
            this.toolStripSeparator4 = new System.Windows.Forms.ToolStripSeparator();
            this.toolStripButton删除线 = new System.Windows.Forms.ToolStripButton();
            this.toolStripButton删除面 = new System.Windows.Forms.ToolStripButton();
            this.toolStripSeparator5 = new System.Windows.Forms.ToolStripSeparator();
            this.toolStripComboBox线快查 = new System.Windows.Forms.ToolStripComboBox();
            this.toolStripButton线快查 = new System.Windows.Forms.ToolStripButton();
            this.toolStripComboBox面快查 = new System.Windows.Forms.ToolStripComboBox();
            this.toolStripButton面快查 = new System.Windows.Forms.ToolStripButton();
            this.toolStripComboBox1属性添加线 = new System.Windows.Forms.ToolStripComboBox();
            this.toolStripComboBox1属性添加面 = new System.Windows.Forms.ToolStripComboBox();
            this.mainmenustrip.SuspendLayout();
            this.panelbackground.SuspendLayout();
            this.maintoolstrip.SuspendLayout();
            this.SuspendLayout();
            // 
            // mainmenustrip
            // 
            this.mainmenustrip.GripMargin = new System.Windows.Forms.Padding(2, 2, 0, 2);
            this.mainmenustrip.ImageScalingSize = new System.Drawing.Size(24, 24);
            this.mainmenustrip.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.文件ToolStripMenuItem,
            this.操作ToolStripMenuItem,
            this.查询ToolStripMenuItem,
            this.编辑ToolStripMenuItem});
            this.mainmenustrip.Location = new System.Drawing.Point(0, 0);
            this.mainmenustrip.Name = "mainmenustrip";
            this.mainmenustrip.Size = new System.Drawing.Size(1092, 32);
            this.mainmenustrip.TabIndex = 0;
            this.mainmenustrip.Text = "mainmenustrip";
            // 
            // 文件ToolStripMenuItem
            // 
            this.文件ToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.打开ToolStripMenuItem});
            this.文件ToolStripMenuItem.Name = "文件ToolStripMenuItem";
            this.文件ToolStripMenuItem.Size = new System.Drawing.Size(62, 28);
            this.文件ToolStripMenuItem.Text = "文件";
            // 
            // 打开ToolStripMenuItem
            // 
            this.打开ToolStripMenuItem.Name = "打开ToolStripMenuItem";
            this.打开ToolStripMenuItem.Size = new System.Drawing.Size(146, 34);
            this.打开ToolStripMenuItem.Text = "打开";
            this.打开ToolStripMenuItem.Click += new System.EventHandler(this.打开ToolStripMenuItem_Click);
            // 
            // 操作ToolStripMenuItem
            // 
            this.操作ToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.放大ToolStripMenuItem,
            this.缩小ToolStripMenuItem,
            this.漫游ToolStripMenuItem,
            this.全图ToolStripMenuItem});
            this.操作ToolStripMenuItem.Name = "操作ToolStripMenuItem";
            this.操作ToolStripMenuItem.Size = new System.Drawing.Size(62, 28);
            this.操作ToolStripMenuItem.Text = "操作";
            // 
            // 放大ToolStripMenuItem
            // 
            this.放大ToolStripMenuItem.Name = "放大ToolStripMenuItem";
            this.放大ToolStripMenuItem.Size = new System.Drawing.Size(146, 34);
            this.放大ToolStripMenuItem.Text = "放大";
            this.放大ToolStripMenuItem.Click += new System.EventHandler(this.放大ToolStripMenuItem_Click);
            // 
            // 缩小ToolStripMenuItem
            // 
            this.缩小ToolStripMenuItem.Name = "缩小ToolStripMenuItem";
            this.缩小ToolStripMenuItem.Size = new System.Drawing.Size(146, 34);
            this.缩小ToolStripMenuItem.Text = "缩小";
            this.缩小ToolStripMenuItem.Click += new System.EventHandler(this.缩小ToolStripMenuItem_Click);
            // 
            // 漫游ToolStripMenuItem
            // 
            this.漫游ToolStripMenuItem.Name = "漫游ToolStripMenuItem";
            this.漫游ToolStripMenuItem.Size = new System.Drawing.Size(146, 34);
            this.漫游ToolStripMenuItem.Text = "漫游";
            this.漫游ToolStripMenuItem.Click += new System.EventHandler(this.漫游ToolStripMenuItem_Click);
            // 
            // 全图ToolStripMenuItem
            // 
            this.全图ToolStripMenuItem.Name = "全图ToolStripMenuItem";
            this.全图ToolStripMenuItem.Size = new System.Drawing.Size(146, 34);
            this.全图ToolStripMenuItem.Text = "全图";
            this.全图ToolStripMenuItem.Click += new System.EventHandler(this.全图ToolStripMenuItem_Click);
            // 
            // 查询ToolStripMenuItem
            // 
            this.查询ToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.线查询ToolStripMenuItem,
            this.面查询ToolStripMenuItem});
            this.查询ToolStripMenuItem.Name = "查询ToolStripMenuItem";
            this.查询ToolStripMenuItem.Size = new System.Drawing.Size(62, 28);
            this.查询ToolStripMenuItem.Text = "查询";
            // 
            // 线查询ToolStripMenuItem
            // 
            this.线查询ToolStripMenuItem.Name = "线查询ToolStripMenuItem";
            this.线查询ToolStripMenuItem.Size = new System.Drawing.Size(164, 34);
            this.线查询ToolStripMenuItem.Text = "线查询";
            this.线查询ToolStripMenuItem.Click += new System.EventHandler(this.线查询ToolStripMenuItem_Click);
            // 
            // 面查询ToolStripMenuItem
            // 
            this.面查询ToolStripMenuItem.Name = "面查询ToolStripMenuItem";
            this.面查询ToolStripMenuItem.Size = new System.Drawing.Size(164, 34);
            this.面查询ToolStripMenuItem.Text = "面查询";
            this.面查询ToolStripMenuItem.Click += new System.EventHandler(this.面查询ToolStripMenuItem_Click);
            // 
            // 编辑ToolStripMenuItem
            // 
            this.编辑ToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.添加线ToolStripMenuItem,
            this.添加面ToolStripMenuItem,
            this.删除线ToolStripMenuItem,
            this.删除面ToolStripMenuItem});
            this.编辑ToolStripMenuItem.Name = "编辑ToolStripMenuItem";
            this.编辑ToolStripMenuItem.Size = new System.Drawing.Size(62, 28);
            this.编辑ToolStripMenuItem.Text = "编辑";
            // 
            // 添加线ToolStripMenuItem
            // 
            this.添加线ToolStripMenuItem.Name = "添加线ToolStripMenuItem";
            this.添加线ToolStripMenuItem.Size = new System.Drawing.Size(164, 34);
            this.添加线ToolStripMenuItem.Text = "添加线";
            this.添加线ToolStripMenuItem.Click += new System.EventHandler(this.添加线ToolStripMenuItem_Click);
            // 
            // 添加面ToolStripMenuItem
            // 
            this.添加面ToolStripMenuItem.Name = "添加面ToolStripMenuItem";
            this.添加面ToolStripMenuItem.Size = new System.Drawing.Size(164, 34);
            this.添加面ToolStripMenuItem.Text = "添加面";
            this.添加面ToolStripMenuItem.Click += new System.EventHandler(this.添加面ToolStripMenuItem_Click);
            // 
            // 删除线ToolStripMenuItem
            // 
            this.删除线ToolStripMenuItem.Name = "删除线ToolStripMenuItem";
            this.删除线ToolStripMenuItem.Size = new System.Drawing.Size(164, 34);
            this.删除线ToolStripMenuItem.Text = "删除线";
            this.删除线ToolStripMenuItem.Click += new System.EventHandler(this.删除线ToolStripMenuItem_Click);
            // 
            // 删除面ToolStripMenuItem
            // 
            this.删除面ToolStripMenuItem.Name = "删除面ToolStripMenuItem";
            this.删除面ToolStripMenuItem.Size = new System.Drawing.Size(164, 34);
            this.删除面ToolStripMenuItem.Text = "删除面";
            this.删除面ToolStripMenuItem.Click += new System.EventHandler(this.删除面ToolStripMenuItem_Click);
            // 
            // panelbackground
            // 
            this.panelbackground.Controls.Add(this.mainpanel);
            this.panelbackground.Controls.Add(this.maintoolstrip);
            this.panelbackground.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelbackground.Location = new System.Drawing.Point(0, 32);
            this.panelbackground.Margin = new System.Windows.Forms.Padding(4);
            this.panelbackground.Name = "panelbackground";
            this.panelbackground.Size = new System.Drawing.Size(1092, 360);
            this.panelbackground.TabIndex = 1;
            // 
            // mainpanel
            // 
            this.mainpanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.mainpanel.Location = new System.Drawing.Point(0, 38);
            this.mainpanel.Margin = new System.Windows.Forms.Padding(4);
            this.mainpanel.Name = "mainpanel";
            this.mainpanel.Size = new System.Drawing.Size(1092, 322);
            this.mainpanel.TabIndex = 1;
            this.mainpanel.Paint += new System.Windows.Forms.PaintEventHandler(this.mainpanel_Paint);
            this.mainpanel.MouseDoubleClick += new System.Windows.Forms.MouseEventHandler(this.mainpanel_MouseDoubleClick_1);
            this.mainpanel.MouseDown += new System.Windows.Forms.MouseEventHandler(this.mainpanel_MouseDown);
            this.mainpanel.MouseEnter += new System.EventHandler(this.mainpanel_MouseEnter);
            this.mainpanel.MouseMove += new System.Windows.Forms.MouseEventHandler(this.mainpanel_MouseMove);
            this.mainpanel.MouseUp += new System.Windows.Forms.MouseEventHandler(this.mainpanel_MouseUp);
            this.mainpanel.MouseWheel += new System.Windows.Forms.MouseEventHandler(this.mainpanel_MouseWheel);
            // 
            // maintoolstrip
            // 
            this.maintoolstrip.ImageScalingSize = new System.Drawing.Size(24, 24);
            this.maintoolstrip.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripButton打开,
            this.toolStripSeparator1,
            this.toolStripButton箭头,
            this.toolStripButton放大,
            this.toolStripButton缩小,
            this.toolStripButton漫游,
            this.toolStripButton全图,
            this.toolStripSeparator2,
            this.toolStripButton线查询,
            this.toolStripButton面查询,
            this.toolStripSeparator3,
            this.toolStripButton添加线,
            this.toolStripButton添加面,
            this.toolStripSeparator4,
            this.toolStripButton删除线,
            this.toolStripButton删除面,
            this.toolStripSeparator5,
            this.toolStripComboBox线快查,
            this.toolStripButton线快查,
            this.toolStripComboBox面快查,
            this.toolStripButton面快查,
            this.toolStripComboBox1属性添加线,
            this.toolStripComboBox1属性添加面});
            this.maintoolstrip.Location = new System.Drawing.Point(0, 0);
            this.maintoolstrip.Name = "maintoolstrip";
            this.maintoolstrip.Padding = new System.Windows.Forms.Padding(0, 0, 3, 0);
            this.maintoolstrip.Size = new System.Drawing.Size(1092, 38);
            this.maintoolstrip.TabIndex = 0;
            this.maintoolstrip.Text = "maintoolstrip";
            // 
            // toolStripButton打开
            // 
            this.toolStripButton打开.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton打开.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton打开.Image")));
            this.toolStripButton打开.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton打开.Name = "toolStripButton打开";
            this.toolStripButton打开.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton打开.Text = "打开";
            this.toolStripButton打开.Click += new System.EventHandler(this.toolStripButton打开_Click);
            // 
            // toolStripSeparator1
            // 
            this.toolStripSeparator1.Name = "toolStripSeparator1";
            this.toolStripSeparator1.Size = new System.Drawing.Size(6, 38);
            // 
            // toolStripButton箭头
            // 
            this.toolStripButton箭头.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton箭头.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton箭头.Image")));
            this.toolStripButton箭头.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton箭头.Name = "toolStripButton箭头";
            this.toolStripButton箭头.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton箭头.Text = "箭头";
            this.toolStripButton箭头.Click += new System.EventHandler(this.toolStripButton箭头_Click);
            // 
            // toolStripButton放大
            // 
            this.toolStripButton放大.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton放大.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton放大.Image")));
            this.toolStripButton放大.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton放大.Name = "toolStripButton放大";
            this.toolStripButton放大.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton放大.Text = "放大";
            this.toolStripButton放大.Click += new System.EventHandler(this.toolStripButton放大_Click);
            // 
            // toolStripButton缩小
            // 
            this.toolStripButton缩小.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton缩小.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton缩小.Image")));
            this.toolStripButton缩小.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton缩小.Name = "toolStripButton缩小";
            this.toolStripButton缩小.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton缩小.Text = "缩小";
            this.toolStripButton缩小.Click += new System.EventHandler(this.toolStripButton缩小_Click);
            // 
            // toolStripButton漫游
            // 
            this.toolStripButton漫游.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton漫游.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton漫游.Image")));
            this.toolStripButton漫游.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton漫游.Name = "toolStripButton漫游";
            this.toolStripButton漫游.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton漫游.Text = "漫游";
            this.toolStripButton漫游.Click += new System.EventHandler(this.toolStripButton漫游_Click);
            // 
            // toolStripButton全图
            // 
            this.toolStripButton全图.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton全图.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton全图.Image")));
            this.toolStripButton全图.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton全图.Name = "toolStripButton全图";
            this.toolStripButton全图.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton全图.Text = "全图";
            this.toolStripButton全图.Click += new System.EventHandler(this.toolStripButton全图_Click);
            // 
            // toolStripSeparator2
            // 
            this.toolStripSeparator2.Name = "toolStripSeparator2";
            this.toolStripSeparator2.Size = new System.Drawing.Size(6, 38);
            // 
            // toolStripButton线查询
            // 
            this.toolStripButton线查询.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton线查询.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton线查询.Image")));
            this.toolStripButton线查询.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton线查询.Name = "toolStripButton线查询";
            this.toolStripButton线查询.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton线查询.Text = "线查询";
            this.toolStripButton线查询.Click += new System.EventHandler(this.toolStripButton线查询_Click);
            // 
            // toolStripButton面查询
            // 
            this.toolStripButton面查询.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton面查询.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton面查询.Image")));
            this.toolStripButton面查询.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton面查询.Name = "toolStripButton面查询";
            this.toolStripButton面查询.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton面查询.Text = "面查询";
            this.toolStripButton面查询.Click += new System.EventHandler(this.toolStripButton面查询_Click);
            // 
            // toolStripSeparator3
            // 
            this.toolStripSeparator3.Name = "toolStripSeparator3";
            this.toolStripSeparator3.Size = new System.Drawing.Size(6, 38);
            // 
            // toolStripButton添加线
            // 
            this.toolStripButton添加线.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton添加线.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton添加线.Image")));
            this.toolStripButton添加线.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton添加线.Name = "toolStripButton添加线";
            this.toolStripButton添加线.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton添加线.Text = "添加线";
            this.toolStripButton添加线.Click += new System.EventHandler(this.toolStripButton添加线_Click);
            // 
            // toolStripButton添加面
            // 
            this.toolStripButton添加面.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton添加面.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton添加面.Image")));
            this.toolStripButton添加面.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton添加面.Name = "toolStripButton添加面";
            this.toolStripButton添加面.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton添加面.Text = "添加面";
            this.toolStripButton添加面.Click += new System.EventHandler(this.toolStripButton添加面_Click);
            // 
            // toolStripSeparator4
            // 
            this.toolStripSeparator4.Name = "toolStripSeparator4";
            this.toolStripSeparator4.Size = new System.Drawing.Size(6, 38);
            // 
            // toolStripButton删除线
            // 
            this.toolStripButton删除线.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton删除线.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton删除线.Image")));
            this.toolStripButton删除线.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton删除线.Name = "toolStripButton删除线";
            this.toolStripButton删除线.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton删除线.Text = "删除线";
            this.toolStripButton删除线.Click += new System.EventHandler(this.toolStripButton删除线_Click);
            // 
            // toolStripButton删除面
            // 
            this.toolStripButton删除面.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton删除面.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton删除面.Image")));
            this.toolStripButton删除面.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton删除面.Name = "toolStripButton删除面";
            this.toolStripButton删除面.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton删除面.Text = "删除面";
            this.toolStripButton删除面.Click += new System.EventHandler(this.toolStripButton删除面_Click);
            // 
            // toolStripSeparator5
            // 
            this.toolStripSeparator5.Name = "toolStripSeparator5";
            this.toolStripSeparator5.Size = new System.Drawing.Size(6, 38);
            // 
            // toolStripComboBox线快查
            // 
            this.toolStripComboBox线快查.Name = "toolStripComboBox线快查";
            this.toolStripComboBox线快查.Size = new System.Drawing.Size(136, 38);
            this.toolStripComboBox线快查.Click += new System.EventHandler(this.toolStripComboBox线快查_Click);
            // 
            // toolStripButton线快查
            // 
            this.toolStripButton线快查.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton线快查.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton线快查.Image")));
            this.toolStripButton线快查.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton线快查.Name = "toolStripButton线快查";
            this.toolStripButton线快查.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton线快查.Text = "toolStripButton1";
            this.toolStripButton线快查.Click += new System.EventHandler(this.toolStripButton线快查_Click);
            // 
            // toolStripComboBox面快查
            // 
            this.toolStripComboBox面快查.Name = "toolStripComboBox面快查";
            this.toolStripComboBox面快查.Size = new System.Drawing.Size(136, 38);
            this.toolStripComboBox面快查.Click += new System.EventHandler(this.toolStripComboBox面快查_Click);
            // 
            // toolStripButton面快查
            // 
            this.toolStripButton面快查.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this.toolStripButton面快查.Image = ((System.Drawing.Image)(resources.GetObject("toolStripButton面快查.Image")));
            this.toolStripButton面快查.ImageTransparentColor = System.Drawing.Color.Magenta;
            this.toolStripButton面快查.Name = "toolStripButton面快查";
            this.toolStripButton面快查.Size = new System.Drawing.Size(34, 33);
            this.toolStripButton面快查.Text = "toolStripButton2";
            this.toolStripButton面快查.Click += new System.EventHandler(this.toolStripButton面快查_Click);
            // 
            // toolStripComboBox1属性添加线
            // 
            this.toolStripComboBox1属性添加线.Name = "toolStripComboBox1属性添加线";
            this.toolStripComboBox1属性添加线.Size = new System.Drawing.Size(92, 38);
            this.toolStripComboBox1属性添加线.Click += new System.EventHandler(this.toolStripComboBox1属性添加线_Click);
            // 
            // toolStripComboBox1属性添加面
            // 
            this.toolStripComboBox1属性添加面.Name = "toolStripComboBox1属性添加面";
            this.toolStripComboBox1属性添加面.Size = new System.Drawing.Size(92, 38);
            this.toolStripComboBox1属性添加面.Click += new System.EventHandler(this.toolStripComboBox1属性添加面_Click);
            // 
            // GISForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1092, 392);
            this.Controls.Add(this.panelbackground);
            this.Controls.Add(this.mainmenustrip);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MainMenuStrip = this.mainmenustrip;
            this.Margin = new System.Windows.Forms.Padding(4);
            this.Name = "GISForm";
            this.Text = "AsiaGIS";
            this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
            this.mainmenustrip.ResumeLayout(false);
            this.mainmenustrip.PerformLayout();
            this.panelbackground.ResumeLayout(false);
            this.panelbackground.PerformLayout();
            this.maintoolstrip.ResumeLayout(false);
            this.maintoolstrip.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.MenuStrip mainmenustrip;
        private System.Windows.Forms.ToolStripMenuItem 文件ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 打开ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 操作ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 放大ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 缩小ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 漫游ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 全图ToolStripMenuItem;
        private System.Windows.Forms.Panel panelbackground;
        private System.Windows.Forms.Panel mainpanel;
        private System.Windows.Forms.ToolStrip maintoolstrip;
        private System.Windows.Forms.ToolStripButton toolStripButton打开;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator1;
        private System.Windows.Forms.ToolStripButton toolStripButton放大;
        private System.Windows.Forms.ToolStripButton toolStripButton缩小;
        private System.Windows.Forms.ToolStripButton toolStripButton漫游;
        private System.Windows.Forms.ToolStripButton toolStripButton全图;
        private System.Windows.Forms.ToolStripMenuItem 查询ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 线查询ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 面查询ToolStripMenuItem;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator2;
        private System.Windows.Forms.ToolStripButton toolStripButton线查询;
        private System.Windows.Forms.ToolStripButton toolStripButton面查询;
        private System.Windows.Forms.ToolStripMenuItem 编辑ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 添加线ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 添加面ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 删除线ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 删除面ToolStripMenuItem;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator3;
        private System.Windows.Forms.ToolStripButton toolStripButton添加线;
        private System.Windows.Forms.ToolStripButton toolStripButton添加面;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator4;
        private System.Windows.Forms.ToolStripButton toolStripButton删除线;
        private System.Windows.Forms.ToolStripButton toolStripButton删除面;
        private System.Windows.Forms.ToolStripButton toolStripButton箭头;
        private System.Windows.Forms.ToolStripComboBox toolStripComboBox线快查;
        private System.Windows.Forms.ToolStripComboBox toolStripComboBox面快查;
        private System.Windows.Forms.ToolStripButton toolStripButton线快查;
        private System.Windows.Forms.ToolStripButton toolStripButton面快查;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator5;
        private System.Windows.Forms.ToolStripComboBox toolStripComboBox1属性添加线;
        private System.Windows.Forms.ToolStripComboBox toolStripComboBox1属性添加面;
    }
}

