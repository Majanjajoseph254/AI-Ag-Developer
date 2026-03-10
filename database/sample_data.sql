INSERT INTO users (name, email, password_hash, role) VALUES
('John Kamau', 'john@example.com', '$2b$12$eSc2FGqMrqRRzuyKgLHPnuyg19Ip2OpkJrDjc8ppGt2nOPz7/rHfu', 'farmer'),
('Mary Wanjiku', 'mary@example.com', '$2b$12$eSc2FGqMrqRRzuyKgLHPnuyg19Ip2OpkJrDjc8ppGt2nOPz7/rHfu', 'farmer'),
('Admin User', 'admin@example.com', '$2b$12$eSc2FGqMrqRRzuyKgLHPnuyg19Ip2OpkJrDjc8ppGt2nOPz7/rHfu', 'admin')
ON CONFLICT (email) DO NOTHING;

INSERT INTO crops (user_id, crop_name, growth_stage, planting_date, fertilizer_used, notes) VALUES
(1, 'Maize', 'Vegetative', '2026-01-15', 'DAP', 'First season planting'),
(1, 'Tomatoes', 'Flowering', '2026-02-01', 'NPK 17:17:17', 'Greenhouse tomatoes'),
(1, 'Potatoes', 'Seedling', '2026-02-20', 'CAN', 'Irish potatoes variety'),
(2, 'Wheat', 'Vegetative', '2026-01-10', 'Urea', 'Rain-fed wheat'),
(2, 'Maize', 'Fruiting', '2025-12-01', 'DAP + CAN', 'Irrigated maize');

INSERT INTO crops (user_id, crop_name, growth_stage, disease_detected, treatment, date_logged) VALUES
(1, 'Maize', 'Vegetative', 'Northern Leaf Blight', 'Apply fungicide (e.g., azoxystrobin). Remove infected leaves.', '2026-02-15'),
(2, 'Tomatoes', 'Flowering', 'Early Blight', 'Apply copper-based fungicide. Remove lower affected leaves.', '2026-02-20');

INSERT INTO market (user_id, crop_name, location, price_per_kg, contact_info, description) VALUES
(1, 'Maize', 'Nairobi', 45.00, '+254712345678', 'Fresh maize from Kiambu county'),
(1, 'Tomatoes', 'Nakuru', 80.00, '+254712345678', 'Grade A tomatoes, greenhouse grown'),
(2, 'Potatoes', 'Nyandarua', 35.00, '+254723456789', 'Irish potatoes, bulk available'),
(2, 'Wheat', 'Narok', 55.00, '+254723456789', 'Wheat grain ready for milling');

INSERT INTO community_posts (user_id, title, content, category) VALUES
(1, 'Best maize varieties for highland areas?', 'I farm in Nyandarua and looking for maize varieties that do well at high altitude. Any recommendations?', 'Crop Tips'),
(2, 'Tips for organic tomato farming', 'Ive been growing tomatoes organically for 3 seasons. Happy to share tips and answer questions!', 'Crop Tips'),
(1, 'Market prices dropping - what to do?', 'Maize prices have dropped significantly this season. How are other farmers coping?', 'Market Info');

INSERT INTO community_replies (post_id, user_id, content) VALUES
(1, 2, 'Try H614D or KH600 varieties. They perform well in cool highland areas above 1800m.'),
(2, 1, 'Thanks for sharing! What pest control methods do you use for organic tomatoes?');
