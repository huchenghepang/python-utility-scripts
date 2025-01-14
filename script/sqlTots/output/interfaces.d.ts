export type Tables = 'Permissions' | 'RolePermissions' | 'Roles' |
'UserRoles' | 'article_categories' | 'comment_likes' | 'comments' |
'files_info' | 'note_tags' | 'notes' | 'sessions' | 'tags' |
'user_comments' | 'user_info';
export interface Permissions {
  // 源表名称: Permissions - 主键: `permission_id`
  /** 无描述 可选 - 自增长  */
  permission_id?: number;
  /** 无描述 必填   */
  permission_name: string;
  /** 无描述 可选  - 默认 */
  description?: string;
  /** 无描述 必填   */
  type: 'route' | 'button';
  /** 无描述 可选  - 默认 */
  parent_id?: number;
  /** 无描述 可选  - 默认 */
  can_delete?: number;
  /** 无描述 可选  - 默认 */
  permission_value?: string;
}

export interface Rolepermissions {
  // 源表名称: RolePermissions - 主键: `role_id`, `permission_id`
  /** 无描述 必填   */
  role_id: number;
  /** 无描述 必填   */
  permission_id: number;
}

export interface Roles {
  // 源表名称: Roles - 主键: `role_id`
  /** 无描述 可选 - 自增长  */
  role_id?: number;
  /** 无描述 必填   */
  role_name: string;
  /** 无描述 可选  - 默认 */
  description?: string;
  /** 自动得到创建的时间 可选  - 默认 */
  created_at?: string;
  /** 更新时得到时间 可选  - 默认 */
  updated_at?: string;
}

export interface Userroles {
  // 源表名称: UserRoles - 主键: `user_id`, `role_id`
  /** 无描述 必填   */
  user_id: string;
  /** 无描述 必填   */
  role_id: number;
}

export interface ArticleCategories {
  // 源表名称: article_categories - 主键: `id`, `name`
  /** 分类id 可选 - 自增长  */
  id?: number;
  /** 分类名 必填   */
  name: string;
  /** 上级分类id 可选  - 默认 */
  parent_id?: number;
  /** 分类的级别 必填   */
  level: number;
  /** 分类的详细信息 可选  - 默认 */
  slug?: string;
  /** 分类的创建时间 可选  - 默认 */
  created_at?: string;
  /** 分类的更新时间 可选  - 默认 */
  updated_at?: string;
}

export interface CommentLikes {
  // 源表名称: comment_likes - 主键: `like_id`
  /** 喜欢的评论Id 可选 - 自增长  */
  like_id?: number;
  /** 用户名创建评论的 必填   */
  user_id: string;
  /** 喜欢的评论id 必填   */
  comment_id: number;
  /** 评论的创建时间 可选  - 默认 */
  created_at?: string;
}

export interface Comments {
  // 源表名称: comments - 主键: `comment_id`, `article_id`, `user_id`
  /** 评论的id 可选 - 自增长  */
  comment_id?: number;
  /** 文章的id 必填   */
  article_id: number;
  /** 用户的id 必填   */
  user_id: string;
  /** 父级id 可选  - 默认 */
  parent_id?: number;
  /** 评论的详情 必填   */
  content: string;
  /** 评论的创建时间 可选  - 默认 */
  created_at?: string;
  /** 评论的更新时间 可选  - 默认 */
  updated_at?: string;
  /** 评论的状态 默认pending 可选  - 默认 */
  status?: 'pending' | 'approved' | 'rejected';
  /** 评论被喜欢的数量 可选  - 默认 */
  like_count?: number;
  /** 评论的被回复数量 可选  - 默认 */
  reply_count?: number;
}

export interface FilesInfo {
  // 源表名称: files_info - 主键: `file_id` DESC
  /** 文件名 必填   */
  file_name: string;
  /** 文件id 可选 - 自增长  */
  file_id?: number;
  /** 文件路径 必填   */
  file_path: string;
  /** 文件后缀 必填   */
  file_ext: string;
  /** 文件上传时间 可选  - 默认 */
  upload_time?: string;
  /** 文件的类型（MIME类型） 必填   */
  file_type: string;
  /** 文件的大小 必填   */
  file_size: number;
  /** 文件全名 必填   */
  file_fullname: string;
  /** 用户id 可选  - 默认 */
  user_id?: string;
  /** 文件的哈希值 必填   */
  hash: string;
  /** 文件的状态 必填   */
  status: 'active' | 'inactive' | 'deleted';
  /** 文件的描述 可选   */
  description?: string;
}

export interface NoteTags {
  // 源表名称: note_tags - 主键: `note_id`, `tag_id`
  /** 无描述 必填   */
  note_id: number;
  /** 无描述 必填   */
  tag_id: number;
}

export interface Notes {
  // 源表名称: notes - 主键: `id`
  /** 无描述 可选 - 自增长  */
  id?: number;
  /** 无描述 必填   */
  name: string;
  /** 无描述 必填   */
  category_id: number;
  /** 无描述 必填   */
  file_id: number;
  /** 无描述 可选  - 默认 */
  created_at?: string;
  /** 无描述 必填   */
  create_time: string;
  /** 无描述 可选  - 默认 */
  is_archive?: number;
  /** 文档的摘要 可选   */
  summary?: string;
  /** 文档的目录 可选   */
  toc?: any;
  /** 无描述 可选  - 默认 */
  reading?: number;
  /** 无描述 可选  - 默认 */
  updated_time?: string;
  /** 无描述 可选  - 默认 */
  comment_count?: number;
}

export interface Sessions {
  // 源表名称: sessions - 主键: `session_id`
  /** 无描述 必填   */
  session_id: string;
  /** 无描述 必填   */
  expires: number;
  /** 无描述 可选   */
  data?: string;
}

export interface Tags {
  // 源表名称: tags - 主键: `id` DESC
  /** 无描述 可选 - 自增长  */
  id?: number;
  /** 无描述 必填   */
  name: string;
}

export interface UserComments {
  // 源表名称: user_comments - 主键: `id` DESC, `user_id`, `comment_id`
  /** 无描述 可选 - 自增长  */
  id?: number;
  /** 无描述 必填   */
  user_id: string;
  /** 无描述 必填   */
  comment_id: number;
  /** 无描述 可选  - 默认 */
  liked?: 'false' | 'true';
  /** 无描述 可选  - 默认 */
  report?: 'true' | 'false';
  /** 无描述 必填   */
  commented: 'true' | 'false';
}

export interface UserInfo {
  // 源表名称: user_info - 主键: `user_id`
  /** 序号 可选 - 自增长  */
  index?: number;
  /** 用户ID 可选  - 默认 */
  user_id?: string;
  /** 账号 必填   */
  account: string;
  /** 密码\r\n 必填   */
  password: string;
  /** 无描述 可选  - 默认 */
  register_datetime?: string;
  /** 是否登录 可选  - 默认 */
  is_login?: number;
  /** 是否注销了账号 可选  - 默认 */
  is_delete?: number;
  /** 用户别名 可选  - 默认 */
  username?: string;
  /** 用户角色\r\n 可选  - 默认 */
  role?: string;
  /** 用户的头像 可选  - 默认 */
  avatar?: string;
  /** 用户的邮箱 可选  - 默认 */
  email?: string;
  /** 用户的个性签名 可选  - 默认 */
  signature?: string;
}
