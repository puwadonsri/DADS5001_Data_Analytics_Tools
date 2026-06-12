import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# Thai font setup
font_path = r'C:\Windows\Fonts\tahoma.ttf'
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Tahoma'
else:
    plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

CHARTS_DIR = os.path.join(os.path.dirname(__file__), 'charts')

df_project = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Dataset', 'opendata_project.csv'))
df_unittype = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Dataset', 'opendata_unittype.csv'))
df_train = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Dataset', 'opendata_train_station.csv'))

# Filter: only Bangkok & perimeter + projects with "project_" prefix
mask_province = df_project['province_id'].isin([3781, 3372, 3599, 3498])
mask_project = df_project['project_id'].str.contains("project", na=False)
df_proj_filtered = df_project.loc[mask_province & mask_project]

cols_project = ['project_id', 'name_en', 'name_th', 'propertytype_name_en',
                'propertytype_name_th', 'price_min', 'latitude', 'longitude',
                'province_id', 'province_name_en', 'province_name_th',
                'developer_name_en', 'developer_name_th']
df_proj_filtered = df_proj_filtered[cols_project]

df_ut_filtered = df_unittype[
    df_unittype['propertytype_id'].isin([1, 2, 3, 4, 6, 20000])
]
cols_unittype = ['unittype_id', 'project_id', 'propertytype_id',
                 'propertytype_name_en', 'propertytype_name_th',
                 'area_usable_min', 'price_min']
df_ut_filtered = df_ut_filtered[cols_unittype]

df_merged = pd.merge(df_proj_filtered, df_ut_filtered, how='inner', on='project_id')

# ============================================================
# Chart 1: Average Price by Property Type
# ============================================================
t1 = df_merged.groupby('propertytype_name_th_x')['price_min_y'].mean().sort_values()
names = list(t1.keys())
values = t1.values / 1e6

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(names)), values, color='#2E86AB', edgecolor='white', height=0.6)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=11)
ax.set_xlabel('ราคาเฉลี่ย (ล้านบาท)', fontsize=12)
ax.set_title('ราคาเฉลี่ยของอสังหาริมทรัพย์ตามประเภท', fontsize=14, fontweight='bold')
for i, v in enumerate(values):
    ax.text(v + 0.05, i, f'{v:.2f}M', va='center', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'avg_price_by_type.png'), dpi=150)
plt.close()

# ============================================================
# Chart 2: Average Price by Province
# ============================================================
t2 = df_merged.groupby('province_name_th')['price_min_y'].mean().sort_values()
prov_names = list(t2.keys())
prov_values = t2.values / 1e6

fig, ax = plt.subplots(figsize=(10, 6))
colors_prov = ['#A63A50', '#F0A202', '#2E86AB', '#7E5F5A']
bars = ax.barh(range(len(prov_names)), prov_values, color=colors_prov, edgecolor='white', height=0.5)
ax.set_yticks(range(len(prov_names)))
ax.set_yticklabels(prov_names, fontsize=12)
ax.set_xlabel('ราคาเฉลี่ย (ล้านบาท)', fontsize=12)
ax.set_title('ราคาเฉลี่ยของอสังหาริมทรัพย์ตามจังหวัด', fontsize=14, fontweight='bold')
for i, v in enumerate(prov_values):
    ax.text(v + 0.05, i, f'{v:.2f}M', va='center', fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'avg_price_by_province.png'), dpi=150)
plt.close()

# ============================================================
# Chart 3: Property Type Distribution by Province (stacked bar)
# ============================================================
ct = pd.crosstab(df_merged['province_name_th'], df_merged['propertytype_name_th_x'])
fig, ax = plt.subplots(figsize=(10, 6))
ct.plot(kind='bar', stacked=True, ax=ax, colormap='Set2', edgecolor='white')
ax.set_xlabel('จังหวัด', fontsize=12)
ax.set_ylabel('จำนวนโครงการ', fontsize=12)
ax.set_title('จำนวนโครงการจำแนกตามประเภทอสังหาฯ ในแต่ละจังหวัด', fontsize=13, fontweight='bold')
ax.legend(title='ประเภท', bbox_to_anchor=(1.02, 1))
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'property_distribution.png'), dpi=150)
plt.close()

# ============================================================
# Chart 4: Price Distribution by Type (Box Plot)
# ============================================================
fig, ax = plt.subplots(figsize=(11, 6))
types = df_merged['propertytype_name_th_x'].unique()
data_by_type = [df_merged[df_merged['propertytype_name_th_x'] == t]['price_min_y'].dropna().values / 1e6 for t in types]
bp = ax.boxplot(data_by_type, tick_labels=types, patch_artist=True)
for patch, color in zip(bp['boxes'], plt.cm.Set2(np.linspace(0, 1, len(types)))):
    patch.set_facecolor(color)
ax.set_ylabel('ราคา (ล้านบาท)', fontsize=12)
ax.set_title('การกระจายตัวของราคาอสังหาริมทรัพย์แยกตามประเภท', fontsize=13, fontweight='bold')
ax.set_xticklabels(types, rotation=20, ha='right')
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'price_distribution_boxplot.png'), dpi=150)
plt.close()

# ============================================================
# Chart 5: Top 15 Developers by Number of Projects
# ============================================================
dev_counts = df_proj_filtered['developer_name_en'].dropna().value_counts().head(15)
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(dev_counts)), dev_counts.values, color='#F0A202', edgecolor='white')
ax.set_yticks(range(len(dev_counts)))
ax.set_yticklabels(dev_counts.index, fontsize=9)
ax.set_xlabel('จำนวนโครงการ', fontsize=12)
ax.set_title('ผู้พัฒนาอสังหาริมทรัพย์ที่มีโครงการมากที่สุด 15 อันดับ', fontsize=13, fontweight='bold')
for i, v in enumerate(dev_counts.values):
    ax.text(v + 0.3, i, str(v), va='center', fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'top_developers.png'), dpi=150)
plt.close()

# ============================================================
# Chart 6: Facility Analysis - % of projects with each facility
# ============================================================
facilities = ['facility_clubhouse', 'facility_fitness', 'facility_meeting',
              'facility_park', 'facility_playground', 'facility_pool', 'facility_security']
facility_names_th = ['คลับเฮาส์', 'ฟิตเนส', 'ห้องประชุม', 'สวนสาธารณะ', 'สนามเด็กเล่น', 'สระว่ายน้ำ', 'ระบบรักษาความปลอดภัย']
facility_pcts = [df_project[col].dropna().mean() * 100 for col in facilities]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(facility_names_th)), facility_pcts, color='#2E86AB', edgecolor='white')
ax.set_yticks(range(len(facility_names_th)))
ax.set_yticklabels(facility_names_th, fontsize=11)
ax.set_xlabel('เปอร์เซ็นต์ของโครงการที่มีสิ่งอำนวยความสะดวก (%)', fontsize=12)
ax.set_title('สัดส่วนโครงการที่มีสิ่งอำนวยความสะดวกแต่ละประเภท', fontsize=13, fontweight='bold')
for i, v in enumerate(facility_pcts):
    ax.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'facility_analysis.png'), dpi=150)
plt.close()

# ============================================================
# Chart 7: Average Price by Number of Bedrooms
# ============================================================
if 'count_room_bed' in df_merged.columns:
    df_bed = df_merged[df_merged['count_room_bed'].notna()].copy()
    if not df_bed.empty:
        bed_groups = df_bed.groupby('count_room_bed')['price_min_y'].mean().sort_index()
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(bed_groups.index.astype(int), bed_groups.values / 1e6, marker='o', linewidth=2, color='#A63A50')
        ax.set_xlabel('จำนวนห้องนอน', fontsize=12)
        ax.set_ylabel('ราคาเฉลี่ย (ล้านบาท)', fontsize=12)
        ax.set_title('ความสัมพันธ์ระหว่างจำนวนห้องนอนกับราคาเฉลี่ย', fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        ax.set_xticks(bed_groups.index.astype(int))
        fig.tight_layout()
        fig.savefig(os.path.join(CHARTS_DIR, 'price_by_bedrooms.png'), dpi=150)
        plt.close()

# ============================================================
# Chart 8: Development Trend Over Time
# ============================================================
df_project['year'] = pd.to_datetime(df_project['date_created'], errors='coerce').dt.year
year_counts = df_project['year'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(year_counts.index.astype(int), year_counts.values, color='#7E5F5A', edgecolor='white', width=0.7)
ax.set_xlabel('ปี', fontsize=12)
ax.set_ylabel('จำนวนโครงการที่สร้าง', fontsize=12)
ax.set_title('จำนวนโครงการอสังหาริมทรัพย์ที่สร้างในแต่ละปี', fontsize=13, fontweight='bold')
ax.set_xticks(year_counts.index.astype(int))
ax.tick_params(axis='x', rotation=45)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'development_trend.png'), dpi=150)
plt.close()

# ============================================================
# Chart 9: Price vs Usable Area Scatter (by property type)
# ============================================================
df_scatter = df_merged.dropna(subset=['area_usable_min', 'price_min_y']).copy()
df_scatter['price_per_sqm'] = df_scatter['price_min_y'] / df_scatter['area_usable_min']
fig, ax = plt.subplots(figsize=(10, 6))
for i, ptype in enumerate(df_scatter['propertytype_name_th_x'].unique()):
    subset = df_scatter[df_scatter['propertytype_name_th_x'] == ptype]
    ax.scatter(subset['area_usable_min'], subset['price_min_y'] / 1e6,
               alpha=0.4, s=10, label=ptype, c=plt.cm.Set2(i / 5))
ax.set_xlabel('พื้นที่ใช้สอย (ตร.ม.)', fontsize=12)
ax.set_ylabel('ราคา (ล้านบาท)', fontsize=12)
ax.set_title('ความสัมพันธ์ระหว่างพื้นที่ใช้สอยกับราคา', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'price_vs_area.png'), dpi=150)
plt.close()

# ============================================================
# Chart 10: Number of Train Stations by Railway Line
# ============================================================
line_counts = df_train['line_th'].value_counts()
fig, ax = plt.subplots(figsize=(10, 5))
colors_line = plt.cm.tab10(np.linspace(0, 1, len(line_counts)))
ax.barh(range(len(line_counts)), line_counts.values, color=colors_line, edgecolor='white')
ax.set_yticks(range(len(line_counts)))
ax.set_yticklabels(line_counts.index, fontsize=10)
ax.set_xlabel('จำนวนสถานี', fontsize=12)
ax.set_title('จำนวนสถานีรถไฟฟ้าแยกตามสาย', fontsize=13, fontweight='bold')
for i, v in enumerate(line_counts.values):
    ax.text(v + 0.3, i, str(v), va='center', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS_DIR, 'train_stations_by_line.png'), dpi=150)
plt.close()

print("All charts generated successfully in charts/ folder.")
