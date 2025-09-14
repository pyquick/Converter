# TODO.md

## New Features:
1. 添加了Image Converter设置页面到SettingsDialog
2. 实现了完整的Image Converter设置功能，包含5个设置组：
   - 默认输出格式设置
   - 默认尺寸范围设置  
   - 图像处理选项
   - 界面行为设置
   - 高级选项
3. 在gui_converter.py中集成了QSettings设置管理
4. 实现了load_settings()方法用于加载设置
5. 实现了save_settings()方法用于保存设置

## Bug Fixes:
1. 修复了gui_converter.py中缺少QSettings导入的问题

## Improvements:
1. 扩展了SettingsDialog的自动保存机制以支持Image Converter设置
2. 添加了settings_changed信号用于实时设置保存
3. 实现了完整的设置加载和保存功能
4. 在尺寸变更和格式变更时自动调用save_settings()
5. 应用程序启动时自动加载保存的设置

## Image Converter Settings Details:

### 1. 默认输出格式设置
- 下拉菜单选择默认输出格式（icns、png、jpg、webp、bmp、gif、tiff、ico）
- 默认值：icns

### 2. 默认尺寸范围设置
- 最小尺寸：数字输入框（16-512px）
- 最大尺寸：数字输入框（32-1024px）
- 自动检测：复选框，是否启用自动检测最大尺寸功能

### 3. 图像处理选项
- 保持宽高比：复选框，转换时是否保持原始宽高比
- 自动裁剪为正方形：复选框，对于非正方形图像是否自动裁剪
- 图像质量设置：滑块（1-100），设置JPG/WebP等格式的输出质量

### 4. 界面行为设置
- 自动预览：复选框，选择文件后是否自动显示预览
- 记住上次路径：复选框，是否记住上次选择的输入/输出路径
- 转换完成提示：复选框，转换完成后是否显示成功提示

### 5. 高级选项
- ICNS生成方式：下拉菜单选择使用iconutil（推荐）或Pillow备用方案
- 覆盖确认：复选框，覆盖现有文件前是否提示确认
- 批量处理线程数：数字输入，设置批量转换时的最大线程数（1-8）