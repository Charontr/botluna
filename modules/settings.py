import sqlite3

def initialize_database():
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS server_settings (
                    server_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    kanal_id INTEGER,       
                    prefix TEXT DEFAULT '!',
                    gif_link TEXT,
                    message TEXT,
                    user_role_id INTEGER,
                    bot_role_id INTEGER,
                    moderation_roles TEXT,
                    kullanıcı_role_id INTEGER                   
                )
            ''')

            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS bakiyeler (
                    server_id INTEGER,
                    user_id INTEGER,
                    lunaria INTEGER DEFAULT 0,
                    PRIMARY KEY (server_id, user_id)
                )
            ''')

            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS economy_balances (
                    server_id INTEGER,
                    user_id INTEGER,
                    balance INTEGER,
                    PRIMARY KEY (server_id, user_id)
                )
            ''')

            connection.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Veritabanını başlat
initialize_database()

def set_update_channel(server_id, channel_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, kanal_id)
                VALUES (?, ?)
            ''', (server_id, channel_id))
            connection.commit()
    except Exception as e:
        print(f"Error in set_update_channel: {e}")

def get_update_channel(server_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT kanal_id FROM server_settings WHERE server_id = ?', (server_id,))
            result = cursor.fetchone()

        return result[0] if (result and result[0]) else None
    except Exception as e:
        print(f"Error in get_update_channel: {e}")
        return None

def add_role_to_category(guild_id, category_name, role_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f'''
                UPDATE OR IGNORE server_settings
                SET {category_name}_role_id = COALESCE({category_name}_role_id, ?)
                WHERE server_id = ?
            ''', (role_id, guild_id))
            connection.commit()
    except Exception as e:
        print(f"Hata: {category_name.capitalize()} rolü eklenemedi - {e}")

def get_role(server_id, role_type):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            query = f'SELECT {role_type}_role_id FROM server_settings WHERE server_id = ?'
            parameters = (server_id,)
            result = execute_sql_query(query, parameters)

            fetched_data = result.fetchone()
            return fetched_data[0] if (fetched_data and fetched_data[0]) else None
    except Exception as e:
        print(f"Error in get_{role_type}_role: {e}")
        return None

def execute_sql_query(query, parameters=None):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
                return cursor
            else:
                cursor.execute(query)
                return cursor
    except sqlite3.Error as e:
        print(f"SQLite error in execute_sql_query: {e}")
    except Exception as e:
        print(f"Error in execute_sql_query: {e}")
        return None

def get_prefix(bot, message):
    try:
        if message and message.guild:
            server_id = message.guild.id
            query = 'SELECT prefix FROM server_settings WHERE server_id = ?'
            parameters = (server_id,)
            result = execute_sql_query(query, parameters)

            fetched_data = result.fetchone()
            return fetched_data[0] if (fetched_data and fetched_data[0]) else "!"  # Return fetched prefix or default '!'
    except Exception as e:
        print(f"Error in get_prefix: {e}")
        return "!"

def get_gif_link(server_id):
    try:
        query = 'SELECT gif_link FROM server_settings WHERE server_id = ?'
        parameters = (server_id,)
        result = execute_sql_query(query, parameters)

        fetched_data = result.fetchone()
        return fetched_data[0] if (fetched_data and fetched_data[0]) else "https://tenor.com/oXSlQ1pw1hi.gif"
    except Exception as e:
        print(f"Error in get_gif_link: {e}")
        return "https://tenor.com/oXSlQ1pw1hi.gif"

def set_prefix(server_id, new_prefix):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, prefix)
                VALUES (?, ?)
            ''', (server_id, new_prefix))
            connection.commit()
    except Exception as e:
        print(f"Error in set_prefix: {e}")

def set_gif_link(server_id, new_gif_link):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, gif_link)
                VALUES (?, ?)
            ''', (server_id, new_gif_link))
            connection.commit()
    except Exception as e:
        print(f"Error in set_gif_link: {e}")

def set_welcome_channel(guild_id, channel_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (guild_id, kanal_id)
                VALUES (?, ?)
            ''', (guild_id, channel_id))
            connection.commit()
    except Exception as e:
        print(f"Error in set_welcome_channel: {e}")

def get_welcome_channel(guild_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT kanal_id FROM server_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()

        return result[0] if (result and result[0]) else None
    except Exception as e:
        print(f"Error in get_welcome_channel: {e}")
        return None        
    
def set_welcome_message(guild_id, message):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (guild_id, message)
                VALUES (?, ?)
            ''', (guild_id, message))
            connection.commit()
    except Exception as e:
        print(f"Error in set_welcome_message: {e}")

def get_welcome_message(guild_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT message FROM server_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()

        return result[0] if (result and result[0]) else None
    except Exception as e:
        print(f"Error in get_welcome_message: {e}")
        return None      
    
def set_user_role(server_id, role_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, user_role_id)
                VALUES (?, ?)
            ''', (server_id, role_id))
            connection.commit()
    except Exception as e:
        print(f"Hata: Kullanıcı rolü ayarlanamadı - {e}")

def get_user_role(server_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT user_role_id FROM server_settings WHERE server_id = ?', (server_id,))
            result = cursor.fetchone()

        return result[0] if (result and result[0]) else None
    except Exception as e:
        print(f"Error in get_user_role: {e}")
        return None  

def set_moderation_roles(server_id, roles):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, moderation_roles)
                VALUES (?, ?)
            ''', (server_id, ",".join(map(str, roles))))
            connection.commit()
    except Exception as e:
        print(f"Hata: Moderasyon rolleri ayarlanamadı - {e}")

def get_moderation_roles(server_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT moderation_roles FROM server_settings WHERE server_id = ?', (server_id,))
            result = cursor.fetchone()

        return result[0].split(",") if (result and result[0]) else []
    except Exception as e:
        print(f"Error in get_moderation_roles: {e}")
        return []

def set_bot_role(server_id, role_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, bot_role_id)
                VALUES (?, ?)
            ''', (server_id, role_id))
            connection.commit()
    except Exception as e:
        print(f"Hata: Kullanıcı rolü ayarlanamadı - {e}")

def get_bot_role(server_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT bot_role_id FROM server_settings WHERE server_id = ?', (server_id,))
            result = cursor.fetchone()

        return result[0] if (result and result[0]) else None
    except Exception as e:
        print(f"Error in get_bot_role: {e}")
        return None
    
def set_user_role_command(guild_id, role_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, user_role_id)
                VALUES (?, ?)
            ''', (guild_id, role_id))
            connection.commit()
    except Exception as e:
        print(f"Error in set_user_role_command: {e}")  

def set_bot_role_command(guild_id, role_id):
    try:
        with sqlite3.connect("bot_database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (server_id, bot_role_id)
                VALUES (?, ?)
            ''', (guild_id, role_id))
            connection.commit()
    except Exception as e:
        print(f"Error in set_bot_role_command: {e}")          

async def setup(bot):
    # Veritabanını başlat (bot nesnesine gerek yok)
    initialize_database()