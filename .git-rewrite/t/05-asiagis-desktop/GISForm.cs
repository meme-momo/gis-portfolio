using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.IO;
using System.Windows.Forms;
using System.Drawing.Drawing2D;

namespace AsiaGIS
{
    public partial class GISForm : Form
    {
        public string m_filepath = "";                     //数据文件路径
        public ZBALayer m_ZBAlayer = new ZBALayer();
        public float m_maxX = -99999999;				    //初始化最大最小值
        public float m_minX = 99999999;
        public float m_maxY = -99999999;
        public float m_minY = 99999999;
        public float m_dScale = 0;							//地图比例尺
        public float m_DetaX = 0;					        //地图平移量
        public float m_DetaY = 0;
        public MouseState m_MouseState = MouseState.Free;	//鼠标状态（放大，缩小，漫游）
        public PointF m_DownPoint, m_UpPoint, m_LastPoint;	//鼠标按下，抬起和上一点
        public Bitmap m_bmpbuffer = new Bitmap(100, 100);   //双缓存绘制画布
        public int Distance = 4;                            //线面拾取时的标准距离
        public PointF[] m_Polyline = new PointF[1000];		//折线点数组
        public int m_Pushnum = 0;							//折线点数
        public ZBAPoint[] m_GeoPT = new ZBAPoint[1000];
        public string text1;
        bool isDrag = false;
        Rectangle theRectangle = new Rectangle(new Point(0, 0), new Size(0, 0));
        Point startPoint, startP, oldPoint;
       

 


        public enum MouseState
        {
            Free, ZoomIn, ZoomOut, Pan, QueryLine, QueryArea, AddLine, AddArea,DelLine,DelArea
        }


        public GISForm()
        {
            InitializeComponent();


        }
        //获取ZBA数据外接矩形，并计算屏幕比例尺和屏幕偏移量
        public void GetZBARect()
        {
            //获取panel容器的大小并存入rClient
            RectangleF rClient = new RectangleF(0, 0, mainpanel.Size.Width, mainpanel.Size.Height);
            //设置双缓存画布大小并建立九宫格
            m_bmpbuffer = new Bitmap(mainpanel.Size.Width*3, mainpanel.Size.Height*3);


            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                ZBAList tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;

                    //建立临时xy对象用于比较坐标最大最小值
                    float x = tempzbapt.m_X;
                    float y = tempzbapt.m_Y;
                    //比较大小取最大最小值
                    if (x > m_maxX)
                        m_maxX = x;
                    if (x < m_minX)
                        m_minX = x;
                    if (y > m_maxY)
                        m_maxY = y;
                    if (y < m_minY)
                        m_minY = y;
                }
            }
            

            //计算屏幕比例尺
            float dScaleInX = rClient.Width / (m_maxX - m_minX); 	//x方向比例尺
            float dScaleInY = rClient.Height / (m_maxY - m_minY); 	//y方向比例尺
            m_dScale = dScaleInX < dScaleInY ? dScaleInX : dScaleInY;	//比例尺取x和y方向上比例尺的较小值
            //计算xy方向平移量
            m_DetaX = -m_minX * m_dScale;					//x方向差值
            m_DetaY = m_minY * m_dScale + rClient.Bottom;	//y方向差值
            //使地图位置位于视口中间
            if (m_dScale == dScaleInX)
                m_DetaY += (m_maxY - m_minY) / 2 * m_dScale - rClient.Height / 2;
            else if (m_dScale == dScaleInY)
                m_DetaX += rClient.Width / 2 - (m_maxX - m_minX) / 2 * m_dScale;
        }


        public void GetZBAListMinMax()
        {
            

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                ZBAList tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;

                    //建立临时xy对象用于比较坐标最大最小值
                    float x = tempzbapt.m_X;
                    float y = tempzbapt.m_Y;



                    if (tempzbapt.m_X < ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).min.X)
                        ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).min.X = tempzbapt.m_X;
                    if (tempzbapt.m_X > ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).min.X)
                        ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).max.X = tempzbapt.m_X;
                    if (tempzbapt.m_Y < ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).min.Y)
                        ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).min.Y = tempzbapt.m_Y;
                    if (tempzbapt.m_Y > ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).min.Y)
                        ((ZBAList)m_ZBAlayer.m_ZBAListal[i]).max.Y = tempzbapt.m_Y;
                   
                }
            }
        }


        private void 打开ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //新建打开文件对话框
            OpenFileDialog dlg1 = new OpenFileDialog();
            dlg1.Filter = "文本文件(*.txt)|*.txt";
            //显示打开文件对话框
            if (dlg1.ShowDialog() == DialogResult.OK)
            {
                //获取打开文件路径
                m_filepath = dlg1.FileName;
                //读取ZBA数据
                m_ZBAlayer.ReadZBAData(m_filepath);
                GetZBAListMinMax();
            }
            //获取ZBA数据外接矩形
            GetZBARect();

            //mainpanel刷新重绘
            mainpanel.Refresh();

        }

        private void 放大ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.ZoomIn;
            //设置鼠标为放大镜
            mainpanel.Cursor = new Cursor("放大.ico");


        }

        private void 缩小ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.ZoomOut;
            //设置鼠标为缩小镜
            mainpanel.Cursor = new Cursor("缩小.ico");


        }

        private void 漫游ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.Pan;
            //设置鼠标为手指
            mainpanel.Cursor =new Cursor("漫游.ico ");


        }

        private void 全图ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //获取ZBA数据外接矩形
            GetZBARect();
            //mainpanel刷新重绘
            mainpanel.Refresh();


        }

        private void toolStripButton打开_Click(object sender, EventArgs e)
        {
            //新建打开文件对话框
            OpenFileDialog dlg1 = new OpenFileDialog();
            dlg1.Filter = "文本文件(*.txt)|*.txt";
            //显示打开文件对话框
            if (dlg1.ShowDialog() == DialogResult.OK)
            {
                //获取打开文件路径
                m_filepath = dlg1.FileName;
                //读取ZBA数据
                m_ZBAlayer.ReadZBAData(m_filepath);
                GetZBAListMinMax();
            }
            //获取ZBA数据外接矩形
            GetZBARect();

            //mainpanel刷新重绘
            mainpanel.Refresh();


        }

        private void toolStripButton放大_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.ZoomIn;
            //设置鼠标为放大镜
            mainpanel.Cursor = new Cursor("放大.cur");


        }

        private void toolStripButton缩小_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.ZoomOut;
            //设置鼠标为缩小镜
            mainpanel.Cursor = new Cursor("缩小.cur");


        }

        private void toolStripButton漫游_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.Pan;
            //设置鼠标为手指
            mainpanel.Cursor = new Cursor("漫游.cur");
           

        }

        private void toolStripButton全图_Click(object sender, EventArgs e)
        {
            //获取ZBA数据外接矩形
            GetZBARect();
            //mainpanel刷新重绘
            mainpanel.Refresh();


        }

        private void mainpanel_Paint(object sender, PaintEventArgs e)
        {
            
            
            //获取mainpanel的图形设备环境类
            //Graphics g = e.Graphics;
            Graphics g = Graphics.FromImage(m_bmpbuffer);   //获取双缓存m_bmpbuffer的图形设备环境
            g.Clear(this.BackColor);                        //将m_bmpbuffer用背景色清空，后面的图型绘制都在m_bmpbuffer中绘制

            //定义画笔和画刷
            Pen blackpen = new Pen(Color.Black, 1);
            Pen bluepen = new Pen(Color.Blue, 1);
            Pen redpen = new Pen(Color.Red, 1);
            SolidBrush bluebrush = new SolidBrush(Color.Blue);
            SolidBrush greenbrush = new SolidBrush(Color.Green);

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                ZBAList tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                PointF[] tempptf = new PointF[tempzbalist.m_PointNum];

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量并进行九宫格位移
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX + mainpanel.Width;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY + mainpanel.Height;


                }
               
                //画面
                if (tempzbalist.m_AttributeCode == 3010 ||
                    tempzbalist.m_AttributeCode == 3030)            //水系
                {
                    g.FillPolygon(bluebrush, tempptf);
                }
                else if (tempzbalist.m_AttributeCode == 1000)       //陆地
                {
                    g.FillPolygon(greenbrush, tempptf);
                }
                //画线
                else if (tempzbalist.m_AttributeCode == 3001 ||
                    tempzbalist.m_AttributeCode == 4001)            //强制闭合线
                {
                    g.DrawLines(blackpen, tempptf);
                }
                else if (tempzbalist.m_AttributeCode == 3011 ||
                    tempzbalist.m_AttributeCode == 3031 ||
                    tempzbalist.m_AttributeCode == 3040)            //水系
                {
                    g.DrawLines(bluepen, tempptf);
                }
                else if (tempzbalist.m_AttributeCode == 4010 ||
                    tempzbalist.m_AttributeCode == 4011 ||
                    tempzbalist.m_AttributeCode == 4020)            //国界
                {
                    g.DrawLines(redpen, tempptf);
                }

            }
            //在双缓存m_bmpbuffer中绘制图型完毕，在mainpanel的图型设备环境中将m_bmpbuffer整体绘制出来，将原点移到左上方
            mainpanel.CreateGraphics().DrawImage(m_bmpbuffer, -mainpanel.Width, -mainpanel.Height);


        }
        //mainpanel鼠标按下事件
        private void mainpanel_MouseDown(object sender, MouseEventArgs e)
        {

            //如果按下左键
            if (e.Button == MouseButtons.Left)
            {
                //记录按下点坐标
                m_DownPoint.X = e.X;
                m_DownPoint.Y = e.Y;
                m_LastPoint = m_DownPoint;

                if (m_MouseState == MouseState.ZoomOut || m_MouseState == MouseState.ZoomIn || m_MouseState == MouseState.QueryArea || m_MouseState == MouseState.QueryLine)
                {
                    if (e.Button == MouseButtons.Left)
                    {
                        isDrag = true;
                    }

                    Control control = (Control)sender;

                    // Calculate the startPoint by using the PointToScreen 
                    // method.
                    startPoint = control.PointToScreen(new Point(e.X, e.Y));
                }
                else if (m_MouseState == MouseState.QueryLine)
                {
                    if (m_DownPoint.X == m_UpPoint.X && m_DownPoint.Y == m_UpPoint.Y)
                    {
                        mainpanel.Refresh();                    //重画							
                        ShowLineAttribute(m_DownPoint);			//显示线属性
                    }
                    else
                    {
                        isDrag = false;

                        // Draw the rectangle to be evaluated. Set a dashed frame style 
                        // using the FrameStyle enumeration.
                        ControlPaint.DrawReversibleFrame(theRectangle, this.BackColor, FrameStyle.Dashed);

                        // Find out which controls intersect the rectangle and 
                        // change their color. The method uses the RectangleToScreen  
                        // method to convert the Control's client coordinates 
                        // to screen coordinates.
                        Rectangle controlRectangle;
                        for (int i = 0; i < Controls.Count; i++)
                        {
                            controlRectangle = Controls[i].RectangleToScreen
                                (Controls[i].ClientRectangle);
                            if (controlRectangle.IntersectsWith(theRectangle))
                            {
                                Controls[i].BackColor = Color.BurlyWood;
                            }
                        }

                        // Reset the rectangle
                        theRectangle = new Rectangle(0, 0, 0, 0);
                        mainpanel.Refresh();
                        ShowLineAttributeByRec(m_UpPoint, m_DownPoint);
                    }

                }
                else if (m_MouseState == MouseState.QueryArea)
                {
                    if (m_DownPoint.X == m_UpPoint.X || m_DownPoint.Y == m_UpPoint.Y)
                    {
                        mainpanel.Refresh();                    //重画							
                        ShowAreaAttribute(m_DownPoint);			//显示线属性
                    }
                    else
                    {
                        isDrag = false;

                        // Draw the rectangle to be evaluated. Set a dashed frame style 
                        // using the FrameStyle enumeration.
                        ControlPaint.DrawReversibleFrame(theRectangle, this.BackColor, FrameStyle.Dashed);

                        // Find out which controls intersect the rectangle and 
                        // change their color. The method uses the RectangleToScreen  
                        // method to convert the Control's client coordinates 
                        // to screen coordinates.
                        Rectangle controlRectangle;
                        for (int i = 0; i < Controls.Count; i++)
                        {
                            controlRectangle = Controls[i].RectangleToScreen
                                (Controls[i].ClientRectangle);
                            if (controlRectangle.IntersectsWith(theRectangle))
                            {
                                Controls[i].BackColor = Color.BurlyWood;
                            }
                        }

                        // Reset the rectangle
                        theRectangle = new Rectangle(0, 0, 0, 0);
                        mainpanel.Refresh();
                        ShowAreaAttributeByRect(m_UpPoint, m_DownPoint);
                    }


                }
                //添加线或面
                else if (m_MouseState == MouseState.AddLine)
                {
                    if(toolStripComboBox1属性添加线.Text != "")
                    {
                        if (m_Pushnum == 0)
                        {
                            startP.X = e.X;
                            startP.Y = e.Y+50;
                            oldPoint.X = e.X;
                            oldPoint.Y = e.Y+50;
                            m_Polyline[m_Pushnum].X = e.X;			//将鼠标点击的各点存入数组
                            m_Polyline[m_Pushnum].Y = e.Y;
                            m_Pushnum++;
                        }

                        else
                        {

                            m_Polyline[m_Pushnum].X = e.X;			//将鼠标点击的各点存入数组
                            m_Polyline[m_Pushnum].Y = e.Y;
                            m_Pushnum++;
                            ControlPaint.DrawReversibleLine(PointToScreen(startP), PointToScreen(new Point(e.X, e.Y+50)), this.BackColor);

                            startP.X = e.X;
                            startP.Y = e.Y+50;
                        }

                    }
                    else
                    {
                        MessageBox.Show("未选择创建对象属性", "Zba线对象创建");
                    }
                }
                else if (m_MouseState == MouseState.AddArea)
                {
                    if (toolStripComboBox1属性添加面.Text != "")
                    {
                        if (m_Pushnum == 0)
                        {
                            startP.X = e.X;
                            startP.Y = e.Y+50;
                            oldPoint.X = e.X;
                            oldPoint.Y = e.Y+50;
                            m_Polyline[m_Pushnum].X = e.X;			//将鼠标点击的各点存入数组
                            m_Polyline[m_Pushnum].Y = e.Y;
                            m_Pushnum++;
                        }
                        else
                        {
                            m_Polyline[m_Pushnum].X = e.X;			//将鼠标点击的各点存入数组
                            m_Polyline[m_Pushnum].Y = e.Y;
                            m_Pushnum++;
                            ControlPaint.DrawReversibleLine(PointToScreen(startP), PointToScreen(new Point(e.X, e.Y+50)), this.BackColor);
                            startP.X = e.X;
                            startP.Y = e.Y+50;
                        }
                    }
                    else
                    {
                            MessageBox.Show("未选择创建对象属性", "Zba面对象创建");
                    }
                }

            //删除线
                else if (m_MouseState == MouseState.DelLine)
                {
                    bool flag = false;                              //用于标示是否已经拾取到线并弹出massagebox
                    ZBAList tempzbalist = new ZBAList();            //临时ZBA线面对象
                    PointF[] tempptf = new PointF[0];               //临时数组用于绘制线面
                    Graphics g = mainpanel.CreateGraphics();        //获取panel容器的图形设备环境类
                    //确定取消按钮
                    MessageBoxButtons messButton = MessageBoxButtons.OKCancel;
                    DialogResult dr = MessageBox.Show("是否删除选中的对象?", "提示", messButton);
                    //点击OK按钮
                    if (dr == DialogResult.OK)
                    {
                        //从ZBA层数据中循环取出ZBA线和ZBA面
                        for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
                        {
                            //建立临时ZBA线面对象并赋值
                            tempzbalist = new ZBAList();
                            tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                            //建立临时数组用于绘制线面
                            tempptf = new PointF[tempzbalist.m_PointNum];
                            //从ZBA线面对象中循环取出ZBA点坐标
                            for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                            {
                                //建立临时ZBA点对象并赋值
                                ZBAPoint tempzbapt = new ZBAPoint();
                                tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                                //给临时数组赋值，并附加屏幕比例尺和偏移量
                                tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                                tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                            }

                            if (tempzbalist.m_AttributeCode == 3001 || tempzbalist.m_AttributeCode == 3011 ||
                            tempzbalist.m_AttributeCode == 3031 || tempzbalist.m_AttributeCode == 3040 ||
                            tempzbalist.m_AttributeCode == 4001 || tempzbalist.m_AttributeCode == 4010 ||
                            tempzbalist.m_AttributeCode == 4011 || tempzbalist.m_AttributeCode == 4020)		//如果是线数据
                            {
                                if (CatchLine(tempptf, tempzbalist.m_PointNum, m_DownPoint))	//如果拾取到
                                {
                                    flag = true;
                                    m_ZBAlayer.m_ZBAListal.RemoveAt(i);
                                    mainpanel.Refresh();
                                    break;
                                }
                            }
                        }
                    }
                    else
                    {
                        return;
                    }
                    if (flag == false)   //如果未选中对象，弹框
                        MessageBox.Show("未选中对象", "Zba数据线删除");
                }
                //删除面
                else if (m_MouseState == MouseState.DelArea)
                {
                    bool flag = false;													//用于标示是否已经拾取到面并弹出massagebox
                    ZBAList tempzbalist = new ZBAList();                                //临时ZBA线面对象
                    PointF[] tempptf = new PointF[0];                                   //临时数组用于绘制线面
                    Graphics g = mainpanel.CreateGraphics();                            //获取panel容器的图形设备环境类
                    int times1 = 0, times2 = 0;										//记录面重叠时的位置
                    int t = 0;

                    //从ZBA层数据中循环取出ZBA线和ZBA面
                    for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
                    {
                        if (flag == false)												//如果是还没拾取到
                        {
                            times1++;													//记录第一个面
                            times2++;													//记录第二个面
                        }
                        else															//如果已经拾取到一个面
                        {
                            if (t == 0)
                                times2++;												//记录第二个面
                        }

                        //建立临时ZBA线面对象并赋值
                        tempzbalist = new ZBAList();
                        tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                        //建立临时数组用于绘制线面
                        tempptf = new PointF[tempzbalist.m_PointNum];

                        //从ZBA线面对象中循环取出ZBA点坐标
                        for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                        {
                            //建立临时ZBA点对象并赋值
                            ZBAPoint tempzbapt = new ZBAPoint();
                            tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                            //给临时数组赋值，并附加屏幕比例尺和偏移量
                            tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                            tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                        }
                        if (tempzbalist.m_AttributeCode == 1000 || tempzbalist.m_AttributeCode == 3010 ||
                            tempzbalist.m_AttributeCode == 3030)                        //如果是面数据
                        {
                            if (CatchArea(tempptf, tempzbalist.m_PointNum, m_DownPoint))		//如果拾取到
                            {
                                if (flag == false)                                      //如果还没选中任何面
                                {
                                    t = 0;                                              //标示只拾取到1个面
                                    flag = true;
                                }
                                else
                                {
                                    t = 1;                                              //标示拾取到2个面
                                    break;
                                }
                            }
                        }
                    }
                    //删除面
                    if (flag == false)
                        MessageBox.Show("未选中对象", "Zba数据线属性查询");					//如果未选中对象，弹框
                    else
                    {
                        if (t == 0)                                                         //如果只拾取到1个面
                        {
                            // Initializes the variables to pass to the MessageBox.Show method.
                            string message = "请确认是否删除面";
                            string caption = "确认";
                            MessageBoxButtons buttons = MessageBoxButtons.YesNo;
                            DialogResult result;
                            // Displays the MessageBox.
                            result = MessageBox.Show(message, caption, buttons);

                            if (result == System.Windows.Forms.DialogResult.Yes)
                            {
                                m_ZBAlayer.m_ZBAListal.RemoveAt(times1 - 1);
                            }
                        }
                        else                                                                  //如果拾取到2个面
                        {
                            tempzbalist = m_ZBAlayer.m_ZBAListal[times1 - 1] as ZBAList;      //获取第1个面的点数
                            int num1 = tempzbalist.m_PointNum;
                            tempzbalist = m_ZBAlayer.m_ZBAListal[times2 - 1] as ZBAList;      //获取第2个面的点数
                            int num2 = tempzbalist.m_PointNum;

                            if (num1 < num2)												  //如果第1个面点数少
                            {
                                // Initializes the variables to pass to the MessageBox.Show method.
                                string message = "请确认是否删除面";
                                string caption = "确认";
                                MessageBoxButtons buttons = MessageBoxButtons.YesNo;
                                DialogResult result;
                                // Displays the MessageBox.
                                result = MessageBox.Show(message, caption, buttons);
                                if (result == System.Windows.Forms.DialogResult.Yes)
                                {
                                    m_ZBAlayer.m_ZBAListal.RemoveAt(times1 - 1);                      //取第1个面作为选中的面
                                }
                            }
                            else															    //如果第2个面的点数少
                            {
                                // Initializes the variables to pass to the MessageBox.Show method.
                                string message = "请确认是否删除面";
                                string caption = "确认";
                                MessageBoxButtons buttons = MessageBoxButtons.YesNo;
                                DialogResult result;
                                // Displays the MessageBox.
                                result = MessageBox.Show(message, caption, buttons);
                                if (result == System.Windows.Forms.DialogResult.Yes)
                                {
                                    m_ZBAlayer.m_ZBAListal.RemoveAt(times2 - 1);                //取第2个面作为选中的面
                                }
                            }
                        }
                        mainpanel.Refresh();
                    }
                }
            }
        }

        //mainpanel鼠标抬起事件
        private void mainpanel_MouseUp(object sender, MouseEventArgs e)
        {
           
            m_UpPoint.X = e.X;
            m_UpPoint.Y = e.Y;

            //如果按下左键
            if (e.Button == MouseButtons.Left)
            {
                //漫游
                if (m_MouseState == MouseState.Pan)
                {
                    float nDX = e.X - m_DownPoint.X;		//计算平移量
                    float nDY = e.Y - m_DownPoint.Y;
                    m_DetaX += nDX;
                    m_DetaY += nDY;
                    if (nDX != 0 || nDY != 0)
                    {
                        mainpanel.Refresh();                //mainpanel刷新重绘
                    }
                }
                //放大
                else if (m_MouseState == MouseState.ZoomIn)
                {
                    if (m_DownPoint.X == m_UpPoint.X || m_DownPoint.Y == m_UpPoint.Y)
                    {
                        //点击放大
                        m_dScale = m_dScale * (float)2.0;			//点击时比例尺乘2
                        m_DetaX = mainpanel.Right / 2 - m_DownPoint.X * 2 + m_DetaX * 2;  //计算平移量
                        m_DetaY = mainpanel.Bottom / 2 - m_DownPoint.Y * 2 + m_DetaY * 2;
                    }
                    else
                    {
                        //拉框放大
                        float dScaleInX = Math.Abs((float)(mainpanel.Width) / (float)(m_UpPoint.X - m_DownPoint.X));
                        float dScaleInY = Math.Abs((float)(mainpanel.Height) / (float)(m_UpPoint.Y - m_DownPoint.Y));
                        //计算比例尺
                        float temp_dScale = dScaleInX < dScaleInY ? dScaleInX : dScaleInY;
                        m_dScale *= temp_dScale;
                        //计算平移量
                        m_DetaX = mainpanel.Width / 2 - (m_UpPoint.X + m_DownPoint.X) / 2 * temp_dScale + m_DetaX * temp_dScale;
                        m_DetaY = mainpanel.Height / 2 - (m_UpPoint.Y + m_DownPoint.Y) / 2 * temp_dScale + m_DetaY * temp_dScale;

                        isDrag = false;

                        // Draw the rectangle to be evaluated. Set a dashed frame style 
                        // using the FrameStyle enumeration.
                        ControlPaint.DrawReversibleFrame(theRectangle, this.BackColor, FrameStyle.Dashed);

                        // Find out which controls intersect the rectangle and 
                        // change their color. The method uses the RectangleToScreen  
                        // method to convert the Control's client coordinates 
                        // to screen coordinates.
                        Rectangle controlRectangle;
                        for (int i = 0; i < Controls.Count; i++)
                        {
                            controlRectangle = Controls[i].RectangleToScreen
                                (Controls[i].ClientRectangle);
                            if (controlRectangle.IntersectsWith(theRectangle))
                            {
                                Controls[i].BackColor = Color.BurlyWood;
                            }
                        }

                        // Reset the rectangle.
                        theRectangle = new Rectangle(0, 0, 0, 0);
                        //mainpanel刷新重绘
                        mainpanel.Refresh();
                       

                    }
                   }
                   
                
                //缩小
                else if (m_MouseState == MouseState.ZoomOut)
                {
                    if (m_DownPoint.X == m_UpPoint.X || m_DownPoint.Y == m_UpPoint.Y)
                    {
                        //点击缩小
                        m_dScale = m_dScale / (float)2.0;			//点击时比例尺除2
                        m_DetaX = mainpanel.Right / 2 - m_DownPoint.X / 2 + m_DetaX / 2;  //计算平移量
                        m_DetaY = mainpanel.Bottom / 2 - m_DownPoint.Y / 2 + m_DetaY / 2;
                    }
                    else
                    {
                        //拉框缩小
                        float dScaleInX = Math.Abs((float)(mainpanel.Width) / (float)(m_UpPoint.X - m_DownPoint.X));
                        float dScaleInY = Math.Abs((float)(mainpanel.Height) / (float)(m_UpPoint.Y - m_DownPoint.Y));
                        //计算比例尺
                        float temp_dScale = dScaleInX < dScaleInY ? dScaleInX : dScaleInY;
                        m_dScale /= temp_dScale;
                        //计算平移量
                        m_DetaX = mainpanel.Width / 2 - (m_UpPoint.X + m_DownPoint.X) / 2 / temp_dScale + m_DetaX / temp_dScale;
                        m_DetaY = mainpanel.Height / 2 - (m_UpPoint.Y + m_DownPoint.Y) / 2 / temp_dScale + m_DetaY / temp_dScale;
                        // If the MouseUp event occurs, the user is not dragging.
                        isDrag = false;

                        // Draw the rectangle to be evaluated. Set a dashed frame style 
                        // using the FrameStyle enumeration.
                        ControlPaint.DrawReversibleFrame(theRectangle,
                            this.BackColor, FrameStyle.Dashed);

                        // Find out which controls intersect the rectangle and 
                        // change their color. The method uses the RectangleToScreen  
                        // method to convert the Control's client coordinates 
                        // to screen coordinates.
                        Rectangle controlRectangle;
                        for (int i = 0; i < Controls.Count; i++)
                        {
                            controlRectangle = Controls[i].RectangleToScreen
                                (Controls[i].ClientRectangle);
                            if (controlRectangle.IntersectsWith(theRectangle))
                            {
                                Controls[i].BackColor = Color.BurlyWood;
                            }
                        }

                        // Reset the rectangle.
                        theRectangle = new Rectangle(0, 0, 0, 0);
                        //记录抬起点坐标
                    }
                    //mainpanel刷新重绘
                    mainpanel.Refresh();
                }
                else if (m_MouseState == MouseState.QueryLine)
                {
                    if (m_DownPoint.X == m_UpPoint.X && m_DownPoint.Y == m_UpPoint.Y)
                    {
                        mainpanel.Refresh();                    //重画							
                        ShowLineAttribute(m_DownPoint);			//显示线属性
                    }
                    else
                    {
                        isDrag = false;

                        // Draw the rectangle to be evaluated. Set a dashed frame style 
                        // using the FrameStyle enumeration.
                        ControlPaint.DrawReversibleFrame(theRectangle, this.BackColor, FrameStyle.Dashed);

                        // Find out which controls intersect the rectangle and 
                        // change their color. The method uses the RectangleToScreen  
                        // method to convert the Control's client coordinates 
                        // to screen coordinates.
                        Rectangle controlRectangle;
                        for (int i = 0; i < Controls.Count; i++)
                        {
                            controlRectangle = Controls[i].RectangleToScreen
                                (Controls[i].ClientRectangle);
                            if (controlRectangle.IntersectsWith(theRectangle))
                            {
                                Controls[i].BackColor = Color.BurlyWood;
                            }
                        }

                        // Reset the rectangle
                        theRectangle = new Rectangle(0, 0, 0, 0);
                        mainpanel.Refresh();
                        ShowLineAttributeByRec(m_UpPoint, m_DownPoint);
                    }

                }
                else if (m_MouseState == MouseState.QueryArea)
                {
                    if (m_DownPoint.X == m_UpPoint.X || m_DownPoint.Y == m_UpPoint.Y)
                    {
                        mainpanel.Refresh();                    //重画							
                        ShowAreaAttribute(m_DownPoint);			//显示线属性
                    }
                    else
                    {
                        isDrag = false;

                        // Draw the rectangle to be evaluated. Set a dashed frame style 
                        // using the FrameStyle enumeration.
                        ControlPaint.DrawReversibleFrame(theRectangle, this.BackColor, FrameStyle.Dashed);

                        // Find out which controls intersect the rectangle and 
                        // change their color. The method uses the RectangleToScreen  
                        // method to convert the Control's client coordinates 
                        // to screen coordinates.
                        Rectangle controlRectangle;
                        for (int i = 0; i < Controls.Count; i++)
                        {
                            controlRectangle = Controls[i].RectangleToScreen
                                (Controls[i].ClientRectangle);
                            if (controlRectangle.IntersectsWith(theRectangle))
                            {
                                Controls[i].BackColor = Color.BurlyWood;
                            }
                        }

                        // Reset the rectangle
                        theRectangle = new Rectangle(0, 0, 0, 0);
                        mainpanel.Refresh();
                        ShowAreaAttributeByRect(m_UpPoint, m_DownPoint);
                    }


                }
           }

        }
        //鼠标滚轮事件
        private void mainpanel_MouseWheel(object sender, MouseEventArgs e)
        {
            if (e.Delta == 120)//鼠标滚轮向上滚动1次，放大
            {
                m_dScale = m_dScale * (float)2.0;			//点击时比例尺乘2
                m_DetaX = mainpanel.Right / 2 - mainpanel.Right / 2 * 2 + m_DetaX * 2;  //计算平移量
                m_DetaY = mainpanel.Bottom / 2 - mainpanel.Bottom / 2 * 2 + m_DetaY * 2;
            }
            else if (e.Delta == -120)//鼠标滚轮向下滚动1次，缩小
            {
                m_dScale = m_dScale / (float)2.0;				//点击时比例尺除2
                m_DetaX = mainpanel.Right / 2 - mainpanel.Right / 2 / 2 + m_DetaX / 2;  //计算平移量
                m_DetaY = mainpanel.Bottom / 2 - mainpanel.Bottom / 2 / 2 + m_DetaY / 2;
            }
            mainpanel.Refresh();
        }

        

        //mainpanel鼠标移动事件
        private void mainpanel_MouseMove(object sender, MouseEventArgs e)
        {
           
            float nDX = 0;                                          //鼠标移动时的偏移量
            float nDY = 0;
            Graphics g = Graphics.FromImage(m_bmpbuffer);           //获取双缓存m_bmpbuffer的图形设备环境
            SolidBrush backbrush = new SolidBrush(this.BackColor);  //定义背景颜色的画刷，用于填充漫游时产生的空隙


            if (e.Button == MouseButtons.Left)
            {
                if (m_MouseState == MouseState.Pan)	//漫游
                {
                    nDX = e.X - m_DownPoint.X;		                    //计算平移量
                    nDY = e.Y - m_DownPoint.Y;
                    mainpanel.CreateGraphics().DrawImage(m_bmpbuffer, nDX - mainpanel.Size.Width, nDY - mainpanel.Size.Height);    //将双缓存m_bmpbuffer直接绘制到平移后的位置

                }
                else if (m_MouseState == MouseState.ZoomOut || m_MouseState == MouseState.ZoomIn)
                {
                    if (isDrag)

                    // Hide the previous rectangle by calling the 
                    // DrawReversibleFrame method with the same parameters.
                    {
                        ControlPaint.DrawReversibleFrame(theRectangle,
                            this.BackColor, FrameStyle.Dashed);

                        // Calculate the endpoint and dimensions for the new 
                        // rectangle, again using the PointToScreen method.
                        Point endPoint = ((Control)sender).PointToScreen(new Point(e.X, e.Y));

                        int width = endPoint.X - startPoint.X;
                        int height = endPoint.Y - startPoint.Y;
                        theRectangle = new Rectangle(startPoint.X,
                            startPoint.Y, width, height);

                        // Draw the new rectangle by calling DrawReversibleFrame
                        // again.  
                        ControlPaint.DrawReversibleFrame(theRectangle,
                            this.BackColor, FrameStyle.Dashed);
                    }

                }
                else if (m_MouseState == MouseState.QueryLine || m_MouseState == MouseState.QueryArea)
                {
                    if (isDrag)

                    // Hide the previous rectangle by calling the 
                    // DrawReversibleFrame method with the same parameters.
                    {
                        ControlPaint.DrawReversibleFrame(theRectangle,
                            this.BackColor, FrameStyle.Dashed);

                        // Calculate the endpoint and dimensions for the new 
                        // rectangle, again using the PointToScreen method.
                        Point endPoint = ((Control)sender).PointToScreen(new Point(e.X, e.Y));

                        int width = endPoint.X - startPoint.X;
                        int height = endPoint.Y - startPoint.Y;
                        theRectangle = new Rectangle(startPoint.X,
                            startPoint.Y, width, height);

                        // Draw the new rectangle by calling DrawReversibleFrame
                        // again.  
                        ControlPaint.DrawReversibleFrame(theRectangle,
                            this.BackColor, FrameStyle.Dashed);

                    }
                }



            
            }
            else
            {
                if (m_MouseState == MouseState.AddLine || m_MouseState == MouseState.AddArea)
                {
                    Graphics g1 = CreateGraphics();
                    if (m_Pushnum != 0)
                    {
                        if (oldPoint.X != e.X || oldPoint.Y != e.Y)
                        {
                            //在屏幕上指定的起始点和结束点内绘制具有指定背景色的可逆线
                            //再次绘制同一条线会逆转该方法的结果。使用该方法绘制线类似于反转屏幕的一个区域，
                            //不过它提供了更好的性能适用于更广泛的颜色。

                            ControlPaint.DrawReversibleLine(PointToScreen(startP), PointToScreen(new Point(e.X, e.Y + 50)), this.BackColor);

                            ControlPaint.DrawReversibleLine(PointToScreen(startP), PointToScreen(new Point(e.X, e.Y + 50)), this.BackColor);

                            //存储一个变换的终点，作为下一变换的起点
                            oldPoint.X = e.X;
                            oldPoint.X = e.Y;
                        }







                    }
                    g1.Dispose();
                }


            }
        }

        private void mainpanel_MouseEnter(object sender, EventArgs e)
        {
            //mainpanel获取焦点
            mainpanel.Focus();

        }

        private void toolStripButton线查询_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.QueryLine;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void 线查询ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.QueryLine;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;

        }
        //创建矩形框


        //判断折线是否被拾取
        public bool CatchLine(PointF[] points, int pointnum, PointF point)      //参数为1输入的折线坐标，2折线点数，3鼠标点击坐标
        {
            double d;
            for (int i = 0; i < pointnum - 1; i++)
            {
                if (points[i].X == points[i + 1].X)	        //线段为垂线
                {
                    //拾取点在上下两点之间，且点到线段距离小于DISTANCE时，线目标被拾取
                    if ((point.Y >= Math.Min(points[i].Y, points[i + 1].Y)) && (point.Y <= Math.Max(points[i].Y, points[i + 1].Y)))
                    {
                        d = Math.Abs(points[i].X - point.X);
                        if (d <= Distance)
                            return true;
                    }
                }
                else if (points[i + 1].Y == points[i].Y)    //线段为水平线
                {
                    if (point.X >= Math.Min(points[i].X, points[i + 1].X) && point.X <= Math.Max(points[i].X, points[i + 1].X))
                    {
                        d = Math.Abs(point.Y - points[i].Y);
                        if (d < Distance)
                            return true;
                    }
                }
                else								        //线段为非水平线和非垂直线
                {
                    double xx, yy;						    //xx,yy分别为垂距坐标
                    double k;
                    //左手坐标系(以坐上角点作为原点，x和y互换)
                    k = (points[i + 1].X - points[i].X) * 1.0 / (points[i + 1].Y - points[i].Y);
                    yy = (k / (k * k + 1)) * ((point.X - points[i].X) + point.Y / k + k * points[i].Y);
                    xx = points[i].X + k * (yy - points[i].Y);

                    //垂距在线段内
                    if ((xx >= Math.Min(points[i + 1].X, points[i].X)) && (xx <= Math.Max(points[i + 1].X, points[i].X)) &&
                       (yy >= Math.Min(points[i + 1].Y, points[i].Y)) && (yy <= Math.Max(points[i + 1].Y, points[i].Y)))
                    {
                        d = (point.X - xx) * (point.X - xx) + (point.Y - yy) * (point.Y - yy);
                        if (d <= Distance)
                            return true;
                    }
                }
            }
            return false;														//循环结束，返回FALSE，目标未拾取。
        }
        public bool CatchLineByRec(PointF[] points, int pointnum, PointF Upoint, PointF Dpoint)
        {
            for (int i = 0; i < pointnum - 1; i++)
            {
                if (
                    points[i].X <= Math.Max(Upoint.X, Dpoint.X) &&
                    points[i].X >= Math.Min(Upoint.X, Dpoint.X) &&
                    points[i].Y <= Math.Max(Upoint.Y, Dpoint.Y) &&
                    points[i].Y >= Math.Min(Upoint.Y, Dpoint.Y))
                {

                    return true;

                }
            }
            return false;

        }
        //外接矩形判断折线是否被拾取
        public bool CatchPoint(PointF min, PointF max, PointF point)     //外接矩形的最大最小点以及鼠标点击坐标
        {
            //float wedth = max.X - min.X;
            //float height = min.Y - max.Y;
            //RectangleF thisrectangle = new RectangleF(min.X, max.Y, wedth, height);
            if (point.X <= max.X && point.Y <= max.Y && point.X >= min.X && point.Y >= min.Y)
            {
                return true;
            }
            else
                return false;

        }

        //显示线属性
        public void ShowLineAttribute(PointF point)
        {
            //遍历数据并利用CatchLine函数判断是否拾取到线
            bool flag = false;                              //用于标示是否已经拾取到线并弹出massagebox
            ZBAList tempzbalist = new ZBAList();            //临时ZBA线面对象
            PointF[] tempptf = new PointF[0];               //临时数组用于绘制线面
            Graphics g = mainpanel.CreateGraphics();        //获取panel容器的图形设备环境类

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];
                //对矩形框的最大最小点附加屏幕比例尺和偏移量
                PointF min = new PointF();
                PointF max = new PointF();
                min.X = tempzbalist.min.X * m_dScale + m_DetaX;
                max.X = tempzbalist.max.X * m_dScale + m_DetaX;
                max.Y = tempzbalist.min.Y * (-m_dScale) + m_DetaY;
                min.Y = tempzbalist.max.Y * (-m_dScale) + m_DetaY;

                //tempzbalist.min.X = tempzbalist.min.X * m_dScale + m_DetaX;
                //tempzbalist.max.X = tempzbalist.max.X * m_dScale + m_DetaX;
                //tempzbalist.min.Y = tempzbalist.min.Y * (-m_dScale) + m_DetaY;
                //tempzbalist.max.Y = tempzbalist.max.Y * (-m_dScale) + m_DetaY;

                //tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX + mainpanel.Width;
                //tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY + mainpanel.Height;

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }

                if (tempzbalist.m_AttributeCode == 3001 || tempzbalist.m_AttributeCode == 3011 ||
                    tempzbalist.m_AttributeCode == 3031 || tempzbalist.m_AttributeCode == 3040 ||
                    tempzbalist.m_AttributeCode == 4001 || tempzbalist.m_AttributeCode == 4010 ||
                    tempzbalist.m_AttributeCode == 4011 || tempzbalist.m_AttributeCode == 4020)		//如果是线数据
                {
                    if (CatchPoint(min, max, point))	//如果拾取到
                    {
                        if (CatchLine(tempptf, tempzbalist.m_ZBAPointFal.Count, point))
                        {
                            flag = true;

                            Pen temppen = new Pen(Color.Yellow, 2);         //定义绘制选中线的画笔
                            g.DrawLines(temppen, tempptf);                  //绘制选中的线

                            String attribute = "";                          //临时属性字符串
                            if (tempzbalist.m_AttributeCode == 3001)        //将属性编码和中文属性对应
                                attribute = "强制闭合线";
                            else if (tempzbalist.m_AttributeCode == 3011)
                                attribute = "海岸线";
                            else if (tempzbalist.m_AttributeCode == 3031)
                                attribute = "湖泊水库线";
                            else if (tempzbalist.m_AttributeCode == 3040)
                                attribute = "单线河";
                            else if (tempzbalist.m_AttributeCode == 4001)
                                attribute = "强制闭合线";
                            else if (tempzbalist.m_AttributeCode == 4010)
                                attribute = "陆地国界";
                            else if (tempzbalist.m_AttributeCode == 4011)
                                attribute = "水中国界";
                            else if (tempzbalist.m_AttributeCode == 4020)
                                attribute = "未定国界";

                            //在Massagebox中输出查询到的线的属性
                            String infomation = String.Format("线属性查询\n\n属性码为：{0}\n属性为：   {1}\n点数为：   {2}",
                                tempzbalist.m_AttributeCode, attribute, tempzbalist.m_PointNum);
                            MessageBox.Show(infomation, "Zba数据线属性查询");
                            break;
                        }
                    }

                     
                }
            }
            if (flag == false)   //如果未选中对象，弹框
                MessageBox.Show("未选中对象", "Zba数据线属性查询");									

        }
        public void ShowLineAttributeByRec(PointF Upoint, PointF Dpoint)
        {
            bool flag = false;                              //用于标示是否已经拾取到线并弹出massagebox
            ZBAList tempzbalist = new ZBAList();            //临时ZBA线面对象
            PointF[] tempptf = new PointF[0];               //临时数组用于绘制线面
            Graphics g = mainpanel.CreateGraphics();        //获取panel容器的图形设备环境类

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }
                if (tempzbalist.m_AttributeCode == 3001 || tempzbalist.m_AttributeCode == 3011 ||
                tempzbalist.m_AttributeCode == 3031 || tempzbalist.m_AttributeCode == 3040 ||
                tempzbalist.m_AttributeCode == 4001 || tempzbalist.m_AttributeCode == 4010 ||
                tempzbalist.m_AttributeCode == 4011 || tempzbalist.m_AttributeCode == 4020)		//如果是线数据
                {
                    if (CatchLineByRec(tempptf, tempzbalist.m_PointNum, Upoint, Dpoint))	//如果拾取到
                    {
                        flag = true;

                        Pen temppen = new Pen(Color.Yellow, 2);         //定义绘制选中线的画笔
                        g.DrawLines(temppen, tempptf); //绘制选中的线
                    }
                }


            }
            if (flag == false)   //如果未选中对象，弹框
                MessageBox.Show("未选中对象", "Zba数据线属性查询");
        }


        private void toolStripButton面查询_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.QueryArea;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void 面查询ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.QueryArea;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }
        //判断面是否被拾取
        public bool CatchArea(PointF[] points, int pointnum, PointF point)          //参数为1输入的面边界坐标，2面边界点数，3鼠标点击坐标
        {
            if (pointnum < 3)									//如果点数小于3，则不是面
                return false;
            Region rgn = new Region();                          //定义一个区域region
            GraphicsPath myGraphicsPath = new GraphicsPath();   //定义一个Path路径作为区域的边界
            myGraphicsPath.AddPolygon(points);                  //给路径path赋值为面边界坐标
            rgn.MakeEmpty();                                    //清空区域region
            rgn.Union(myGraphicsPath);                          //给区域region边界赋值为path坐标
            return rgn.IsVisible(point);                        //判断输入点坐标是否在区域region内并返回
        }
        public bool CatchAreaByRect(PointF[] points, int pointnum, PointF Upoint, PointF Dpoint)          //参数为1输入的面边界坐标，2面边界点数，3鼠标点击坐标
        {
            if (pointnum < 3)									//如果点数小于3，则不是面
                //判断输入点坐标是否在区域region内并返回
                for (int i = 0; i < pointnum - 1; i++)
                {
                    if (
                        points[i].X <= Math.Max(Upoint.X, Dpoint.X) &&
                        points[i].X >= Math.Min(Upoint.X, Dpoint.X) &&
                        points[i].Y <= Math.Max(Upoint.Y, Dpoint.Y) &&
                        points[i].Y >= Math.Min(Upoint.Y, Dpoint.Y))
                    {

                        return true;

                    }

                }

            Region rgn = new Region();                          //定义一个区域region
            GraphicsPath myGraphicsPath = new GraphicsPath();   //定义一个Path路径作为区域的边界
            myGraphicsPath.AddPolygon(points);                  //给路径path赋值为面边界坐标
            rgn.MakeEmpty();                                    //清空区域region
            rgn.Union(myGraphicsPath);                          //给区域region边界赋值为path坐标
            return (rgn.IsVisible(Upoint) || rgn.IsVisible(Dpoint));






        }
        //显示面属性
        public void ShowAreaAttribute(PointF point)
        {
            //遍历数据并利用CatchArea函数判断是否拾取到面，并显示其属性
            bool flag = false;													//用于标示是否已经拾取到面并弹出massagebox
            ZBAList tempzbalist = new ZBAList();                                //临时ZBA线面对象
            PointF[] tempptf = new PointF[0];                                   //临时数组用于绘制线面
            Graphics g = mainpanel.CreateGraphics();                            //获取panel容器的图形设备环境类
            int times1 = 0, times2 = 0;										//记录面重叠时的位置
            int t = 0;

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                if (flag == false)												//如果是还没拾取到
                {
                    times1++;													//记录第一个面
                    times2++;													//记录第二个面
                }
                else															//如果已经拾取到一个面
                {
                    if (t == 0)
                        times2++;												//记录第二个面
                }

                //建立临时ZBA线面对象并赋值
                tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }
                if (tempzbalist.m_AttributeCode == 1000 || tempzbalist.m_AttributeCode == 3010 ||
                    tempzbalist.m_AttributeCode == 3030)                        //如果是面数据
                {
                    if (CatchArea(tempptf, tempzbalist.m_PointNum, point))		//如果拾取到
                    {
                        if (flag == false)                                      //如果还没选中任何面
                        {
                            t = 0;                                              //标示只拾取到1个面
                            flag = true;
                        }
                        else
                        {
                            t = 1;                                              //标示拾取到2个面
                            break;
                        }
                    }
                }
            }

            if (flag == false)
                MessageBox.Show("未选中对象", "Zba数据线属性查询");					//如果未选中对象，弹框
            else
            {
                if (t == 0)															//如果只拾取到1个面
                {
                    tempzbalist = new ZBAList();
                    tempzbalist = m_ZBAlayer.m_ZBAListal[times1 - 1] as ZBAList;
                }
                else                                                                //如果拾取到2个面
                {
                    tempzbalist = m_ZBAlayer.m_ZBAListal[times1 - 1] as ZBAList;      //获取第1个面的点数
                    int num1 = tempzbalist.m_PointNum;
                    tempzbalist = m_ZBAlayer.m_ZBAListal[times2 - 1] as ZBAList;      //获取第2个面的点数
                    int num2 = tempzbalist.m_PointNum;

                    if (num1 < num2)												    //如果第1个面点数少
                        tempzbalist = m_ZBAlayer.m_ZBAListal[times1 - 1] as ZBAList;	//取第1个面作为选中的面
                    else															    //如果第2个面的点数少
                        tempzbalist = m_ZBAlayer.m_ZBAListal[times2 - 1] as ZBAList;	//取第2个面作为选中的面
                }

                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;

                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }

                SolidBrush tempbrush = new SolidBrush(Color.Yellow);        //定义绘制选中的面的画刷
                g.FillPolygon(tempbrush, tempptf);                          //绘制选中的面

                String attribute = "";                                      //临时属性字符串
                if (tempzbalist.m_AttributeCode == 1000)                    //将属性编码和中文属性对应
                    attribute = "国家或岛屿";
                else if (tempzbalist.m_AttributeCode == 3010)
                    attribute = "海域";
                else if (tempzbalist.m_AttributeCode == 3030)
                    attribute = "湖泊水库";

                //在Massagebox中输出查询到的面的属性
                String infomation = String.Format("面属性查询\n\n属性码为：{0}\n属性为：   {1}\n点数为：   {2}",
                            tempzbalist.m_AttributeCode, attribute, tempzbalist.m_PointNum);
                MessageBox.Show(infomation, "Zba数据面属性查询");
            }

        }
        public void ShowAreaAttributeByRect(PointF Upoint, PointF Dpoint)
        {
            bool flag = false;                              //用于标示是否已经拾取到线并弹出massagebox
            ZBAList tempzbalist = new ZBAList();            //临时ZBA线面对象
            PointF[] tempptf = new PointF[0];               //临时数组用于绘制线面
            Graphics g = mainpanel.CreateGraphics();        //获取panel容器的图形设备环境类

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }
                if (tempzbalist.m_AttributeCode == 1000 || tempzbalist.m_AttributeCode == 3010 ||
                   tempzbalist.m_AttributeCode == 3030)                        //如果是面数据
                {
                    if (CatchAreaByRect(tempptf, tempzbalist.m_PointNum, Upoint, Dpoint))//如果拾取到
                    {
                        flag = true;
                        SolidBrush tempbrush = new SolidBrush(Color.Yellow);        //定义绘制选中的面的画刷
                        g.FillPolygon(tempbrush, tempptf);


                    }






                }

            }
            if (flag == false)   //如果未选中对象，弹框
                MessageBox.Show("未选中对象", "Zba数据线属性查询");
        }

          
  

        private void 添加线ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.AddLine;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void 添加面ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.AddArea;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void toolStripButton添加线_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.AddLine;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void toolStripButton添加面_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.AddArea;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }
       
        private void toolStripButton删除线_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.DelLine;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void 删除线ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.DelLine;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void 删除面ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.DelArea;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;

        }

        private void toolStripButton删除面_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.DelArea;
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;


        }

        private void toolStripButton箭头_Click(object sender, EventArgs e)
        {
            //设置鼠标状态
            m_MouseState = MouseState.Pan;
            //设置鼠标为箭头
            mainpanel.Cursor =  Cursors.Arrow;
           

        }

        private void mainpanel_MouseDoubleClick_1(object sender, MouseEventArgs e)
        {
            

            //如果按下左键
            if (e.Button == MouseButtons.Left)
            {
                m_GeoPT = new ZBAPoint[m_Pushnum];
                ZBAList tempZbalist = new ZBAList();
                tempZbalist.m_PointNum = m_Pushnum;

                if (m_MouseState == MouseState.AddLine)
                {
                    if (toolStripComboBox1属性添加线.Text == "海岸线")
                    {
                        tempZbalist.m_AttributeCode = 3011;
                    }
                    else if (toolStripComboBox1属性添加线.Text == "陆地国界")
                    {
                        tempZbalist.m_AttributeCode = 4010;
                    }
                    else if (toolStripComboBox1属性添加线.Text == "强制闭合线")
                    {
                        tempZbalist.m_AttributeCode = 3001;

                    }
                    else if (toolStripComboBox1属性添加线.Text == "湖泊水库线")
                    {
                        tempZbalist.m_AttributeCode = 3031;

                    }
                    else if (toolStripComboBox1属性添加线.Text == "单线河")
                    {
                        tempZbalist.m_AttributeCode = 3040;

                    }
                    else if (toolStripComboBox1属性添加线.Text == "海洋国界")
                    {
                        tempZbalist.m_AttributeCode = 4011;

                    }
                    else if (toolStripComboBox1属性添加线.Text == "未定国界")
                    {
                        tempZbalist.m_AttributeCode = 4020;

                    }

                    for (int i = 0; i < m_Pushnum; i++)
                    {
                        m_GeoPT[i] = new ZBAPoint();
                        m_GeoPT[i].m_X = (float)((m_Polyline[i].X - m_DetaX) / m_dScale);
                        m_GeoPT[i].m_Y = (float)((m_Polyline[i].Y - m_DetaY) / (-m_dScale));
                        tempZbalist.m_ZBAPointFal.Add(m_GeoPT[i]);
                    }
                    m_ZBAlayer.m_ZBAListal.Add(tempZbalist);
                    m_Pushnum = 0;
                    mainpanel.Refresh();
                }
                if (m_MouseState == MouseState.AddArea)
                {
                    if (toolStripComboBox1属性添加面.Text == "国家或岛屿")
                    {
                        tempZbalist.m_AttributeCode = 1000;
                    }
                    else if (toolStripComboBox1属性添加面.Text == "海域")
                    {
                        tempZbalist.m_AttributeCode = 3010;
                    }
                    else if (toolStripComboBox1属性添加面.Text == "湖泊水库")
                    {
                        tempZbalist.m_AttributeCode = 3030;

                    }
                    for (int i = 0; i < m_Pushnum; i++)
                    {
                        m_GeoPT[i] = new ZBAPoint();
                        m_GeoPT[i].m_X = (float)((m_Polyline[i].X - m_DetaX) / m_dScale);
                        m_GeoPT[i].m_Y = (float)((m_Polyline[i].Y - m_DetaY) / (-m_dScale));
                        tempZbalist.m_ZBAPointFal.Add(m_GeoPT[i]);
                    }

                    m_ZBAlayer.m_ZBAListal.Add(tempZbalist);
                    m_Pushnum = 0;
                    mainpanel.Refresh();
                }
            }
        }

        private void toolStripComboBox线快查_Click(object sender, EventArgs e)
        {
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;
           
            this.toolStripComboBox线快查.Items.Clear();
            this.toolStripComboBox线快查.Items.Add("强制闭合线");
            this.toolStripComboBox线快查.Items.Add("海岸线");
            this.toolStripComboBox线快查.Items.Add("湖泊水库线");
            this.toolStripComboBox线快查.Items.Add("单线河");
            this.toolStripComboBox线快查.Items.Add("陆地国界");
            this.toolStripComboBox线快查.Items.Add("海洋国界");
            this.toolStripComboBox线快查.Items.Add("未定国界");
        }

        private void toolStripComboBox面快查_Click(object sender, EventArgs e)
        {
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;
           
            this.toolStripComboBox面快查.Items.Clear();
            this.toolStripComboBox面快查.Items.Add("国家或岛屿");
            this.toolStripComboBox面快查.Items.Add("海域");
            this.toolStripComboBox面快查.Items.Add("湖泊水库");
        }

        private void toolStripButton线快查_Click(object sender, EventArgs e)
        {
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;
           
             mainpanel.Refresh();
            bool flag = false;                              //用于标示是否已经拾取到线并弹出massagebox
            ZBAList tempzbalist = new ZBAList();            //临时ZBA线面对象
            PointF[] tempptf = new PointF[0];               //临时数组用于绘制线面
            Graphics g = mainpanel.CreateGraphics();        //获取panel容器的图形设备环境类

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                //建立临时ZBA线面对象并赋值
                tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }

                Pen temppen = new Pen(Color.Yellow, 2);         //定义绘制选中线的画笔
                if (toolStripComboBox线快查.Text == "强制闭合线" && tempzbalist.m_AttributeCode == 3001 || tempzbalist.m_AttributeCode == 4001)
                {
                    g.DrawLines(temppen, tempptf);
                }
                else if (toolStripComboBox线快查.Text == "海岸线" && tempzbalist.m_AttributeCode == 3011)
                {
                    g.DrawLines(temppen, tempptf);
                }
                else if (toolStripComboBox线快查.Text == "湖泊水库线" && tempzbalist.m_AttributeCode == 3031)
                {
                    g.DrawLines(temppen, tempptf);
                }
                else if (toolStripComboBox线快查.Text == "单线河" && tempzbalist.m_AttributeCode == 3040)
                {
                    g.DrawLines(temppen, tempptf);
                }
                else if (toolStripComboBox线快查.Text == "海洋国界" && tempzbalist.m_AttributeCode == 4011)
                {
                    g.DrawLines(temppen, tempptf);
                }
                else if (toolStripComboBox线快查.Text == "陆地国界" && tempzbalist.m_AttributeCode == 4010)
                {
                    g.DrawLines(temppen, tempptf);
                }
                else if (toolStripComboBox线快查.Text == "未定国界" && tempzbalist.m_AttributeCode == 4020)
                {
                    g.DrawLines(temppen, tempptf);
                }
            }
        }

        private void toolStripButton面快查_Click(object sender, EventArgs e)
        {
            //设置鼠标为箭头
            mainpanel.Cursor = Cursors.Arrow;
           
            mainpanel.Refresh();
            bool flag = false;													//用于标示是否已经拾取到面并弹出massagebox
            ZBAList tempzbalist = new ZBAList();                                //临时ZBA线面对象
            PointF[] tempptf = new PointF[0];                                   //临时数组用于绘制线面
            Graphics g = mainpanel.CreateGraphics();                            //获取panel容器的图形设备环境类
            int times1 = 0, times2 = 0;										//记录面重叠时的位置
            int t = 0;

            //从ZBA层数据中循环取出ZBA线和ZBA面
            for (int i = 0; i < m_ZBAlayer.m_ZBAListal.Count; i++)
            {
                if (flag == false)												//如果是还没拾取到
                {
                    times1++;													//记录第一个面
                    times2++;													//记录第二个面
                }
                else															//如果已经拾取到一个面
                {
                    if (t == 0)
                        times2++;												//记录第二个面
                }

                //建立临时ZBA线面对象并赋值
                tempzbalist = new ZBAList();
                tempzbalist = m_ZBAlayer.m_ZBAListal[i] as ZBAList;
                //建立临时数组用于绘制线面
                tempptf = new PointF[tempzbalist.m_PointNum];

                //从ZBA线面对象中循环取出ZBA点坐标
                for (int j = 0; j < tempzbalist.m_ZBAPointFal.Count; j++)
                {
                    //建立临时ZBA点对象并赋值
                    ZBAPoint tempzbapt = new ZBAPoint();
                    tempzbapt = tempzbalist.m_ZBAPointFal[j] as ZBAPoint;
                    //给临时数组赋值，并附加屏幕比例尺和偏移量
                    tempptf[j].X = tempzbapt.m_X * m_dScale + m_DetaX;
                    tempptf[j].Y = tempzbapt.m_Y * (-m_dScale) + m_DetaY;
                }
                SolidBrush tempbrush = new SolidBrush(Color.Yellow);
                if (toolStripComboBox面快查.Text == "国家或岛屿" && tempzbalist.m_AttributeCode == 1000)
                {
                    g.FillPolygon(tempbrush, tempptf);
                }
                if (toolStripComboBox面快查.Text == "海域" && tempzbalist.m_AttributeCode == 3010)
                {
                    g.FillPolygon(tempbrush, tempptf);
                }
                if (toolStripComboBox面快查.Text == "湖泊水库" && tempzbalist.m_AttributeCode == 3030)
                {
                    g.FillPolygon(tempbrush, tempptf);
                }
            }
        }

        private void toolStripComboBox1属性添加线_Click(object sender, EventArgs e)
        {
            this.toolStripComboBox1属性添加线.Items.Clear();
            this.toolStripComboBox1属性添加线.Items.Add("强制闭合线");
            this.toolStripComboBox1属性添加线.Items.Add("海岸线");
            this.toolStripComboBox1属性添加线.Items.Add("湖泊水库线");
            this.toolStripComboBox1属性添加线.Items.Add("单线河");
            this.toolStripComboBox1属性添加线.Items.Add("海洋国界");
            this.toolStripComboBox1属性添加线.Items.Add("陆地国界");
            this.toolStripComboBox1属性添加线.Items.Add("未定国界");
        }

        private void toolStripComboBox1属性添加面_Click(object sender, EventArgs e)
        {
            this.toolStripComboBox1属性添加面.Items.Clear();
            this.toolStripComboBox1属性添加面.Items.Add("国家或岛屿");
            this.toolStripComboBox1属性添加面.Items.Add("海域");
            this.toolStripComboBox1属性添加面.Items.Add("湖泊水库");
        }

      

       






    }

}
            

