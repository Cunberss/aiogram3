from sqlalchemy import select, insert, desc, and_, update, delete

from src.config import PER_PAGE
from src.db import SubCategory, Product, Category, User
from src.db.base import get_session
from src.db.models import Question, Cart, CartItem, Order


async def db_get_subcategories(category_id: int, page=1):
    async with get_session() as session:
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        query = select(SubCategory).where(SubCategory.category_id == category_id).slice(start, end)
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_get_products(subcategory_id: int):
    async with get_session() as session:
        query = select(Product).where(Product.subcategory_id == subcategory_id)
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_get_categories(page=1):
    async with get_session() as session:
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        query = select(Category).slice(start, end)
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_add_user(user_id, username):
    async with get_session() as session:
        user_exists = await session.get(User, user_id)
        if not user_exists:
            stmt = insert(User).values(user_id=user_id, username=username)
            await session.execute(stmt)
            await session.commit()


async def db_get_question(tag_search):
    async with get_session() as session:
        query = select(Question).where(Question.question_text.ilike(f'%{tag_search}%'))
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_get_cart(user_id: int):
    async with get_session() as session:
        query = select(Cart).where(Cart.user_id == user_id)
        result = await session.execute(query)
        answer = result.all()

        if not answer:
            query = insert(Cart).values(user_id=user_id)
        await session.execute(query)
        await session.commit()

        query = select(Cart).where(Cart.user_id == user_id)
        result = await session.execute(query)
        cart_id = int(result.all()[0][0].id)
    return cart_id


async def db_get_cartitems(cart_id):
    async with get_session() as session:
        query = select(Product.name, CartItem.quantity, (Product.price * CartItem.quantity).label('total_price')).join(
            CartItem, Product.id == CartItem.product_id).filter(CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_get_paid_orders(user_id):
    async with get_session() as session:
        query = select(Order.id, Order.price, Order.address).where(and_(Order.user_id == user_id, Order.status == True)).limit(5).order_by(desc(Order.id))
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_update_phone(user_id: int, phone):
    async with get_session() as session:
        query = update(User).where(User.user_id == user_id).values(phone=phone)
        await session.execute(query)
        await session.commit()


async def db_get_cartitems_short(cart_id):
    async with get_session() as session:
        query = select(CartItem.product_id, CartItem.quantity, (Product.price * CartItem.quantity).label('total_price'),
                       Product.name).join(CartItem, Product.id == CartItem.product_id).filter(
            CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_create_order(user_id, address, price, products):
    async with get_session() as session:
        query = insert(Order).values(user_id=user_id, address=address, price=price, products=products)
        await session.execute(query)
        await session.commit()

        query = select(Order.id).where(and_(Order.user_id == user_id, Order.status == False)).order_by(
            desc(Order.id))
        result = await session.execute(query)
        order_id = result.all()[0][0]
    return order_id


async def db_delete_cart(user_id: int, cart_id: int):
    async with get_session() as session:
        query = delete(CartItem).where(CartItem.cart_id == cart_id)
        await session.execute(query)
        query = delete(Cart).where(Cart.user_id == user_id)
        await session.execute(query)
        await session.commit()


async def db_update_status_order(order_id: int):
    async with get_session() as session:
        query = update(Order).where(Order.id == order_id).values(status=True)
        await session.execute(query)
        await session.commit()


async def db_get_data_order(order_id: int):
    async with get_session() as session:
        query = select(User.user_id, User.username, User.phone, Order.id, Order.price, Order.products).join(Order, User.user_id == Order.user_id).filter(Order.id == order_id)
        result = await session.execute(query)
        answer = result.all()[0]
    return answer


async def db_get_data_products(products_ids: list):
    async with get_session() as session:
        query = select(Product.name, Product.price).filter(Product.id.in_(products_ids))
        result = await session.execute(query)
        answer = [el for el in result.all()]
    return answer


async def db_get_cartitems_count(cart_id: int):
    async with get_session() as session:
        query = select(CartItem).where(CartItem.cart_id == cart_id)
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_add_product_in_cart(cart_id: int, product_id: int, quantity: int):
    async with get_session() as session:
        query = select(CartItem).where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id))
        result = await session.execute(query)
        answer = result.all()
        if not answer:
            query = insert(CartItem).values(cart_id=cart_id, product_id=product_id, quantity=quantity)
        else:
            query = update(CartItem).where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)).values(
                {CartItem.quantity: CartItem.quantity + quantity})
        await session.execute(query)
        await session.commit()


async def db_get_phone(user_id: int):
    async with get_session() as session:
        query = select(User.phone).where(User.user_id == user_id)
        result = await session.execute(query)
        answer = result.all()
        phone = answer[0][0]
    return phone


async def db_get_products_in_cart(cart_id):
    async with get_session() as session:
        query = select(Product.id, Product.name).join(CartItem, Product.id == CartItem.product_id).filter(
            CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
        result = await session.execute(query)
        answer = result.all()
    return answer


async def db_delete_product_in_cart(cart_id, product_id):
    async with get_session() as session:
        query = delete(CartItem).where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id))
        await session.execute(query)
        await session.commit()


async def db_get_order_products(order_id: int):
    async with get_session() as session:
        query = select(Order.products).where(Order.id == order_id)
        result = await session.execute(query)
        answer = result.all()[0][0]
    return answer