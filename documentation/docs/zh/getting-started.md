# 入门

## 简介

`pinmok-content` 是基于 Pinmok 的内容管理应用，适用于网站、小程序或其他需要内容展示的场景。后台负责对文章、单页、分类、标签进行管理，
前端可以通过主题模板渲染页面，也可以通过内置的只读 REST API 获取数据，灵活适配不同的前端技术栈。

安装前请确认 Pinmok 已正确安装并能正常运行，`pinmok-content` 不引入额外的环境要求。

## 安装

进入 Django 项目虚拟环境，执行：

```bash
pip install pinmok-content
```

## 配置

### settings.py

将 `pinmok.content` 加入 `INSTALLED_APPS`，位置在 `pinmok.padmin` 之后任意位置：

```python title="settings.py"
INSTALLED_APPS = [
    'pinmok.padmin',
    'pinmok.content',
    # ...
]
```

### urls.py

在项目的 `urls.py` 中添加路由：

```python title="urls.py"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pinmok.content.urls')),  # 添加这里
    # ...
]
```

> **注意：** 如果使用非空前缀，例如 `path('content/', include('pinmok.content.urls'))`，则所有 URL 包括 REST API 均会在该前缀下，API 地址将相应变为
`/content/api/articles/` 等。

## 迁移

执行数据库迁移：

```bash
python manage.py migrate
```

## 同步菜单

启动服务后登录 Pinmok 后台，点击左侧菜单栏顶部的同步菜单按钮（☰），完成同步后内容管理菜单将以正确的名称和图标显示。

---

安装完成，你可以开始使用 pinmok-content 了。