using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Collections;
using System.Drawing;



namespace AsiaGIS
{
    //ZBA点类
    public class ZBAPoint
    {
        public float m_X;
        public float m_Y;
    }

    //ZBA线面类
    public class ZBAList
    {
        public int m_AttributeCode;					        //属性码
        public int m_PointNum;						        //点数
        public ArrayList m_ZBAPointFal = new ArrayList();   //ZBA点数据链表
        public PointF min = new PointF(9999, 9999);
        public PointF max = new PointF(-9999, -9999);
    }


    public class ZBALayer
    {
        public ArrayList m_ZBAListal = new ArrayList();     //ZBA线面数据链表
        public void ReadZBAData(string filepath)
        {
            ZBAList tempZbalist = new ZBAList();
            int j = 0;
             
            if (filepath != "")
            {
                string[] lines = File.ReadAllLines(filepath, Encoding.ASCII);
                if (lines.Length != 0)
                {
                    for (int i = 0; i < lines.Length; i++)
                    {
                        string line = lines[i];
                        string[] strArray = line.Split(' ', '\t');
                         if (strArray[0] == "3010" || strArray[0] == "3030" || strArray[0] == "1000" ||
                            strArray[0] == "3011" || strArray[0] == "3031" || strArray[0] == "3040" ||
                            strArray[0] == "4010" || strArray[0] == "4011" || strArray[0] == "4020" ||
                            strArray[0] == "3001" || strArray[0] == "4001" || strArray[0] == "0" ||
                            strArray[0] == "-99")
                        {
                            tempZbalist = new ZBAList();
                            tempZbalist.m_AttributeCode = int.Parse(strArray[0]);
                            tempZbalist.m_PointNum = int.Parse(strArray[2]);
                            j = 0;
                        }
                         else
                        {
                            ZBAPoint temppoint = new ZBAPoint();
                            temppoint.m_X = float.Parse(strArray[0]);
                            temppoint.m_Y = float.Parse(strArray[3]);
                            tempZbalist.m_ZBAPointFal.Add(temppoint);
                            j++;

                            if (j == tempZbalist.m_PointNum)
                            {
                                m_ZBAListal.Add(tempZbalist);
                            }
                        }
                    }
                }
            }


        }

        



    }
}
