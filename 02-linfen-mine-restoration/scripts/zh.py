import arcpy
import os

def geojson_to_gdb_arcpy(geojson_path, gdb_path, feature_class_name=None):
    """
    使用ArcPy将GeoJSON转换为文件地理数据库中的要素类
    """
    try:
        # 设置工作空间
        arcpy.env.workspace = gdb_path
        
        # 确定要素类名称
        if feature_class_name is None:
            base_name = os.path.splitext(os.path.basename(geojson_path))[0]
            feature_class_name = base_name.replace('(', '').replace(')', '').replace(' ', '_')
        
        # 完整输出路径
        output_fc = os.path.join(gdb_path, feature_class_name)
        
        # 转换GeoJSON为要素类
        print(f"正在将GeoJSON转换为要素类: {output_fc}")
        arcpy.conversion.JSONToFeatures(geojson_path, output_fc)
        
        print(f"转换成功！要素类: {output_fc}")
        return output_fc
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        return None

# 使用示例
input_geojson = r"F:\linfen\patch\patch2.geojson"
output_gdb = r"F:\linfen\patch\shp.gdb"

print("开始转换...")
result = geojson_to_gdb_arcpy(input_geojson, output_gdb)

if result:
    print(f"\n✅ 转换完成！")
    print(f"要素类位置: {result}")
else:
    print("\n❌ 转换失败")
