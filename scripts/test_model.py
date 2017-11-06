#testing
logging.info("Current test set is made from "+str(len(test_data_list))+" files and has "+str(get_num_samples(test_data_list))+" examples")


my_test_generator=batch_generator(500,test_data_list)
for test_batch in my_test_generator:
   loss=autoencoder.evaluate(test_batch,test_batch,batch_size=50)
   logging.info(str(loss))
