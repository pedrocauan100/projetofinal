CREATE DATABASE IF NOT EXISTS pedrosuperselect;
USE pedrosuperselect;

CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100),
    email VARCHAR(200) UNIQUE NOT NULL,
    senha VARCHAR(300) NOT NULL,
    tipo VARCHAR(50) NOT NULL
);

INSERT INTO usuarios (nome, email, senha, tipo) VALUES 
('Usuário 1', 'usuario@email.com', '123', 'cliente'),
('Admin', 'admin@email.com', '123', 'admin');

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    descricao TEXT,
    imagem VARCHAR(255),
    tipo ENUM('Alimentos Secos e Enlatados', 'Bebidas', 'Higiene e Limpeza', 'Frios e Laticínios', 'Verduras e Frutas', 'Padaria e Confeitaria') NOT NULL,
    validade DATE NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO produtos (nome, preco, descricao, imagem, tipo, validade) VALUES
('Arroz Branco 5kg', 22.39, 'Pacote de arroz branco, ideal para o dia a dia.', 'https://www.sondadelivery.com.br/img.aspx/sku/1000036086/530/7896079431158.png', 'Alimentos Secos e Enlatados', '2025-12-31'),
('Refrigerante Coca Cola 2L', 6.49, 'Refrigerante Coca-Cola, garrafa PET de 2 litros.', 'https://drogariacristal.com/media/catalog/product/cache/dc75f304252411b8c602e1e96d99390d/c/o/coca_cola_2lt-nova.jpg', 'Bebidas', '2025-11-30'),
('Detergente Neutro 500ml', 2.99, 'Detergente líquido neutro para louças', 'https://tb0932.vtexassets.com/arquivos/ids/169546/Detergente%20Neutro%20500ml%20Ype%20101095.png.png?v=638773003324270000', 'Higiene e Limpeza', '2025-06-30'),
('Queijo Mussarela Fatiado 1kg', 41.50, 'Queijo mussarela fatiado, ideal para lanches.', 'https://tb1304.vtexassets.com/arquivos/ids/208970-800-800?v=638918689676730000&width=800&height=800&aspect=true', 'Frios e Laticínios', '2025-10-15'),
('Banana', 4.29, 'Banana fresca, ideal para consumo.', 'https://vallefrutas.com.br/wp-content/uploads/banana-nanica.png', 'Verduras e Frutas', '2025-09-20'),
('Pão de Forma Tradicional 500g', 7.49, 'Pão de forma macio, ideal para o café da manhã.', 'https://mambodelivery.vtexassets.com/arquivos/ids/177010/pao-de-forma-tradicional-panco-500g.jpg?v=637883842820430000', 'Padaria e Confeitaria', '2025-09-10');
