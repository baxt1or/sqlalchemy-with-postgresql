from sqlalchemy import URL, create_engine, Column, String, Integer, ForeignKey, DateTime, asc, desc
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from datetime import datetime, timezone
from typing import Generator, List

# Creating the database engine
connection_string = URL.create(
  'postgresql',
  username='neondb_owner',
  password='0bwerTAntPH3',
  host='ep-white-recipe-a5x0smu4.us-east-2.aws.neon.tech',
  database='neondb',
)

try:

  # Ititialing the engine 
  engine = create_engine(connection_string,  connect_args={'sslmode':'require'})
  if engine:
    print("Successfully connected")

except Exception as e:
    print(f"Database Error!")



# ORM Session
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Base declaration for model building
Base = declarative_base()


# Get database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Yield the session for use
    finally:
        db.close()  # Ensure the session is closed



# Database Table Models
class User(Base):
  __tablename__ = "users"

  id = Column("id", Integer, primary_key=True, index=True)
  username = Column("username", String, nullable=False)
  email = Column("email", String, nullable=False)
  name = Column("name", String, nullable=True)
  bio = Column("bio", String, nullable=True)
  created_at = Column(DateTime, default=datetime.now(timezone.utc))

  def __init__(self, username, email, name, bio) -> None:
      self.username = username
      self.email = email
      self.name = name
      self.bio = bio

  def __repr__(self) -> str:
     return f"User: {self.name}, {self.username}, {self.bio}, {self.email}"


class Post(Base):
  __tablename__ = "posts"

  id = Column("id", Integer, primary_key=True, index=True)
  title = Column("title", String, nullable=False)
  content = Column("content", String, nullable=False)

  userId = Column("userId", Integer, ForeignKey("users.id"))
  created_at = Column(DateTime, default=datetime.now(timezone.utc))

  likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

  def __init__(self, title, content, userId) -> None:
     self.title = title
     self.content = content
     self.userId = userId

  def __repr__(self) -> str:
     return f"Post: {self.title}, {self.content}, Owner: {self.userId}"


# Like model
class Like(Base):
  __tablename__ = "likes"
  id = Column("id", Integer, primary_key=True, index=True)
  userId = Column("userId", Integer, ForeignKey("users.id"))
  postId = Column("postId", Integer, ForeignKey("posts.id"))

  post = relationship("Post", back_populates="likes")

  def __init__(self, userId, postId) -> None:
      self.userId = userId
      self.postId = postId



# Queries
def get_user_by_email(email:str, db:Session) -> User:
   user = db.query(User).filter(User.email == email).first()

   return user

def get_users(db:Session, order:str = "asc") -> List[User]:
   
    if order == "asc":
      users :List[User] =  db.query(User).order_by(asc(User.created_at)).all()
    else:
      users :List[User] = db.query(User).order_by(desc(User.created_at)).all()
    
    return users

def get_all_posts(db:Session, order:str = "asc") -> List[Post]:
   
   if order == "asc":
      posts :List[Post] = db.query(Post).order_by(asc(Post.created_at)).all()
   else:
      posts :List[Post] = db.query(Post).order_by(desc(Post.created_at)).all()
   return posts


def get_user_posts(db:Session,userId:int, order:str = "asc") -> List[Post]:
     
    if order == "asc":
       user_posts : List[Post] = db.query(Post).filter(Post.userId == userId).order_by(asc(Post.created_at)).all()
    else:
       user_posts :List[Post] = db.query(Post).filter(Post.userId == userId).order_by(desc(Post.created_at)).all()

    return user_posts


def get_likes_post(postId, db:Session) -> List[Like]:
   
   likes = db.query(Like).filter(Like.postId == postId).all()

   return likes
      


# CRUD of models
def add_user(username:str, email:str, name:str, bio:str, db:Session) -> User:
    
    existing_user :User = get_user_by_email(email=email, db=db)

    if existing_user:
       return None
    
    db_user = User(username=username, email=email, name=name, bio=bio)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_post(title:str, content:str, userId:int, db:Session) -> Post:
   db_post = Post(title=title, content=content, userId=userId)

   db.add(db_post)
   db.commit()
   db.refresh(db_post)

   return db_post
   

def like_post(postId:int, userId:int, db:Session) -> Like:
   db_like : Like = Like(postId=postId, userId=userId)

   db.add(db_like)
   db.commit()
   db.refresh(db_like)

   return db_like


if __name__ == "__main__":
  Base.metadata.create_all(bind=engine)

  username = "alex_123"
  email = "alex@gmail.com"
  name = "Alex Smith"
  bio = "Based in Tashkent"

  title = "CAU is the best"
  content = "Computer Science will change the world for better Economically"
  userId = 1
  postId = 1


  try:
     
    db :Session = next(get_db())

    user :User = add_user(username=username, email=email, name=name, bio=bio, db=db)

    if user:
      print("Successfully added", user.username)
    else:
      print("Faield to add a user") 

    post = create_post(title=title, content=content, userId=userId, db=db)

  
    if post:
      print("Successfully added", post.title)
    else:
      print("Faield to add a user")  

    users : List[User] = get_users(db=db)
    posts : List[Post] = get_all_posts(db=db, order="desc")
    user_posts : List[Post] = get_user_posts(db=db, order="desc", userId=userId)
 
    for user in users:
       print(user)

    for post in posts:
       print(post)

    for u_post in user_posts:
       print(u_post)
     
    like : Like = like_post(userId=userId, postId=postId, db=db)
    likes : List[Like] = get_likes_post(postId=postId, db=db)
      

    if like:
      print("Successfully liked the post")
    else:
      print("Faield to like the post")

    print(f"Likes: {len(likes)}")
  
  finally:
     db.close()